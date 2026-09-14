from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from financeiro.models import ContaReceber
from django.db.models import Sum, Count
from clientes.models import Cliente, Veiculo
from ordens.models import OrdemServico
from produtos.models import Produto


@login_required
def index(request):
    empresa = request.empresa
    atrasados_count = ContaReceber.objects.filter(empresa=empresa, status='atrasado').count()
    context = {
        'atrasados_count': atrasados_count,
    }
    return render(request, 'relatorios/index.html', context)


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
    }

    if request.GET.get('print'):
        return render(request, 'relatorios/print_financeiro.html', context)

    return render(request, 'relatorios/financeiro.html', context)


@login_required
def relatorio_operacional(request, tipo):
    empresa = request.empresa
    if tipo == 'clientes':
        registros = Cliente.objects.filter(empresa=empresa).order_by('nome')
        titulo = 'Relatório de Clientes'
        colunas = ['Nome', 'Documento', 'Telefone', 'Cidade', 'Status']
    elif tipo == 'veiculos':
        registros = Veiculo.objects.filter(cliente__empresa=empresa).select_related('cliente')
        titulo = 'Relatório de Veículos'
        colunas = ['Placa', 'Veículo', 'Cliente', 'Chassi']
    elif tipo == 'estoque':
        registros = Produto.objects.filter(empresa=empresa, tipo='produto').order_by('nome')
        titulo = 'Relatório de Estoque'
        colunas = ['Produto', 'Código', 'Atual', 'Mínimo', 'Situação']
    elif tipo == 'ordens':
        registros = OrdemServico.objects.filter(empresa=empresa).select_related('cliente', 'veiculo')
        titulo = 'Relatório de Ordens de Serviço'
        colunas = ['Número', 'Cliente', 'Veículo', 'Status', 'Total']
    else:
        return redirect('relatorios:index')
    return render(request, 'relatorios/operacional.html', {'tipo': tipo, 'titulo': titulo, 'colunas': colunas, 'registros': registros})
