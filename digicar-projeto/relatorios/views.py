from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from financeiro.models import ContaReceber
from django.db.models import Sum, Count

from core.formatacao import formatar_moeda

from .exportadores import EXPORTADORES, obter_exportador
from .operacionais import obter_criador


@login_required
def index(request):
    from clientes.models import Cliente, Veiculo
    from django.db.models import F
    from ordens.models import OrdemServico
    from produtos.models import Produto

    empresa = request.empresa
    atrasados_count = ContaReceber.objects.filter(empresa=empresa, status='atrasado').count()
    total_atrasado = ContaReceber.objects.filter(empresa=empresa, status='atrasado').aggregate(
        t=Sum(F('valor') - F('valor_pago')))['t'] or 0
    estoque_baixo = Produto.objects.filter(
        empresa=empresa, tipo='produto', ativo=True, estoque_atual__lte=F('estoque_minimo')).count()
    os_abertas = OrdemServico.objects.filter(
        empresa=empresa, status__in=['aberta', 'em_andamento', 'aguardando_peca']).count()

    clientes = Cliente.objects.filter(empresa=empresa, ativo=True).count()
    veiculos = Veiculo.objects.filter(cliente__empresa=empresa).count()

    relatorios = [
        {
            'grupo': 'Financeiro', 'url': 'relatorios:financeiro', 'tipo': None, 'icone': 'bi-cash-stack',
            'titulo': 'Inadimplência', 'descricao': 'Clientes que mais devem e parcelas vencidas.',
            'numero': atrasados_count, 'rotulo': 'em atraso', 'alerta': atrasados_count > 0,
            'detalhe': formatar_moeda(total_atrasado) if atrasados_count else '',
        },
        {
            'grupo': 'Operacional', 'url': 'relatorios:operacional', 'tipo': 'clientes', 'icone': 'bi-people',
            'titulo': 'Clientes', 'descricao': 'Cadastro com documento, contato e situação.',
            'numero': clientes, 'rotulo': 'ativos',
        },
        {
            'grupo': 'Operacional', 'url': 'relatorios:operacional', 'tipo': 'veiculos', 'icone': 'bi-car-front',
            'titulo': 'Veículos', 'descricao': 'Veículos dos clientes com placa, modelo e chassi.',
            'numero': veiculos, 'rotulo': 'cadastrados',
        },
        {
            'grupo': 'Operacional', 'url': 'relatorios:operacional', 'tipo': 'estoque', 'icone': 'bi-box-seam',
            'titulo': 'Estoque', 'descricao': 'Saldo atual e estoque mínimo de cada peça.',
            'numero': estoque_baixo, 'rotulo': 'abaixo do mínimo', 'alerta': estoque_baixo > 0,
        },
        {
            'grupo': 'Operacional', 'url': 'relatorios:operacional', 'tipo': 'ordens', 'icone': 'bi-tools',
            'titulo': 'Ordens de Serviço', 'descricao': 'Serviços por cliente, veículo, status e valor.',
            'numero': os_abertas, 'rotulo': 'em aberto',
        },
    ]
    return render(request, 'relatorios/index.html', {
        'atrasados_count': atrasados_count,
        'relatorios': relatorios,
    })


@login_required
def relatorio_financeiro(request):
    empresa = request.empresa
    devedores = ContaReceber.objects.filter(
        empresa=empresa,
        status='atrasado'
    ).values('cliente__nome').annotate(
        total_devido=Sum('valor'),
        count=Count('id')
    ).order_by('-total_devido')[:10]

    atrasados = ContaReceber.objects.filter(
        empresa=empresa,
        status='atrasado'
    ).select_related('cliente').order_by('vencimento')

    context = {
        'devedores': devedores,
        'atrasados': atrasados,
        'grafico_devedores': {
            'rotulos': [d['cliente__nome'] for d in devedores],
            'valores': [float(d['total_devido']) for d in devedores],
        },
    }

    if request.GET.get('print'):
        return render(request, 'relatorios/print_financeiro.html', context)

    return render(request, 'relatorios/financeiro.html', context)


@login_required
def relatorio_operacional(request, tipo):
    criador = obter_criador(tipo)
    if criador is None:
        return redirect('relatorios:index')
    dados = criador.montar(request.empresa)
    return render(request, 'relatorios/operacional.html', {
        'tipo': tipo,
        'titulo': dados.titulo,
        'colunas': dados.colunas,
        'linhas': dados.linhas,
        'formatos': EXPORTADORES.keys(),
    })


@login_required
def exportar_operacional(request, tipo, formato):
    criador = obter_criador(tipo)
    exportador = obter_exportador(formato)
    if criador is None or exportador is None:
        raise Http404('Relatório ou formato inexistente.')
    return exportador.exportar(criador.montar(request.empresa), f'relatorio_{tipo}')
