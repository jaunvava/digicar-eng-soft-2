from django.views.decorators.http import require_POST
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F
from datetime import date
from .models import ContaReceber, ContaPagar, BaixaContaReceber, BaixaContaPagar
from clientes.consultas import cliente_da_empresa
from core.formatacao import formatar_moeda
from relatorios.exportadores import ExportadorCSV
from relatorios.operacionais import DadosRelatorio
from .facade import FinanceiroFacade
from .pagamentos import formas_pagamento


def _parse_valor(raw):
    try:
        return Decimal(raw.replace('.', '').replace(',', '.').strip())
    except (InvalidOperation, AttributeError):
        return Decimal('0')


@login_required
def contas_receber(request):
    empresa   = request.empresa
    q         = request.GET.get('q', '')
    num_doc   = request.GET.get('num_doc', '')
    status    = request.GET.get('status', '')
    tipo_data = request.GET.get('tipo_data', '')
    data_ini  = request.GET.get('data_ini', '')
    data_fim  = request.GET.get('data_fim', '')

    contas = ContaReceber.objects.filter(empresa=empresa).select_related('cliente')

    hoje = date.today()
    contas.filter(status__in=['pendente', 'parcial'], vencimento__lt=hoje).update(status='atrasado')

    if q:
        contas = contas.filter(cliente__nome__icontains=q)
    if num_doc:
        contas = contas.filter(numero_titulo__icontains=num_doc)
    if status:
        contas = contas.filter(status=status)
    if tipo_data and data_ini:
        contas = contas.filter(**{f'{tipo_data}__gte': data_ini})
    if tipo_data and data_fim:
        contas = contas.filter(**{f'{tipo_data}__lte': data_fim})

    total_pendente = contas.filter(status__in=['pendente', 'parcial']).aggregate(
        t=Sum(F('valor') - F('valor_pago'))
    )['t'] or 0
    total_atrasado = contas.filter(status='atrasado').aggregate(
        t=Sum(F('valor') - F('valor_pago'))
    )['t'] or 0

    return render(request, 'financeiro/contas_receber.html', {
        'contas': contas, 'q': q, 'num_doc': num_doc, 'status': status,
        'tipo_data': tipo_data, 'data_ini': data_ini, 'data_fim': data_fim,
        'total_pendente': total_pendente, 'total_atrasado': total_atrasado,
    })


@login_required
def nova_conta_receber(request):
    empresa  = request.empresa
    if request.method == 'POST':
        try:
            parcelas = int(request.POST.get('parcelas', 1) or 1)
            ContaReceber.objects.create(
                empresa=empresa,
                cliente=cliente_da_empresa(empresa, request.POST.get('cliente')),
                descricao=request.POST.get('descricao', ''),
                numero_titulo=request.POST.get('numero_titulo', ''),
                valor=_parse_valor(request.POST.get('valor', '0')),
                emissao=request.POST.get('emissao') or date.today(),
                vencimento=request.POST.get('vencimento'),
                parcela=f"1/{parcelas}",
                status=request.POST.get('status', 'pendente'),
                observacoes=request.POST.get('observacoes', ''),
            )
            messages.success(request, 'Conta a receber cadastrada!')
            return redirect('financeiro:contas_receber')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'financeiro/form_conta_receber.html', {
        'total_parcelas': 1,
    })


@login_required
def editar_conta_receber(request, pk):
    conta    = get_object_or_404(ContaReceber, pk=pk, empresa=request.empresa)
    empresa  = request.empresa
    if request.method == 'POST':
        try:
            parcelas = int(request.POST.get('parcelas', 1) or 1)
            conta.cliente      = cliente_da_empresa(empresa, request.POST.get('cliente'), permitir=conta.cliente_id)
            conta.descricao    = request.POST.get('descricao', '')
            conta.numero_titulo = request.POST.get('numero_titulo', '')
            conta.valor        = _parse_valor(request.POST.get('valor', '0'))
            conta.emissao      = request.POST.get('emissao') or conta.emissao
            conta.vencimento   = request.POST.get('vencimento') or conta.vencimento
            conta.parcela      = f"1/{parcelas}"
            conta.status       = request.POST.get('status', conta.status)
            conta.observacoes  = request.POST.get('observacoes', '')
            conta.save()
            messages.success(request, 'Conta a receber atualizada!')
            return redirect('financeiro:contas_receber')
        except Exception as e:
            messages.error(request, f'Erro: {e}')

    try:
        total_parcelas = int(conta.parcela.split('/')[-1])
    except (ValueError, AttributeError):
        total_parcelas = 1

    return render(request, 'financeiro/form_conta_receber.html', {
        'conta': conta,
        'total_parcelas': total_parcelas,
    })


@login_required
@require_POST
def excluir_conta_receber(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        conta.delete()
        messages.success(request, 'Conta excluída com sucesso!')
    return redirect('financeiro:contas_receber')


@login_required
def imprimir_conta(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk, empresa=request.empresa)
    return render(request, 'financeiro/imprimir_conta.html', {'conta': conta})


@login_required
def exportar_contas_receber(request):
    empresa   = request.empresa
    q         = request.GET.get('q', '')
    num_doc   = request.GET.get('num_doc', '')
    status    = request.GET.get('status', '')
    tipo_data = request.GET.get('tipo_data', '')
    data_ini  = request.GET.get('data_ini', '')
    data_fim  = request.GET.get('data_fim', '')

    contas = ContaReceber.objects.filter(empresa=empresa).select_related('cliente')
    if q:
        contas = contas.filter(cliente__nome__icontains=q)
    if num_doc:
        contas = contas.filter(numero_titulo__icontains=num_doc)
    if status:
        contas = contas.filter(status=status)
    if tipo_data and data_ini:
        contas = contas.filter(**{f'{tipo_data}__gte': data_ini})
    if tipo_data and data_fim:
        contas = contas.filter(**{f'{tipo_data}__lte': data_fim})

    def data(valor):
        return valor.strftime('%d/%m/%Y') if valor else ''

    def numero(valor):
        return str(valor).replace('.', ',')

    dados = DadosRelatorio(
        titulo='Contas a Receber',
        colunas=['ID', 'Cliente', 'Nº Título', 'Parcela', 'Emissão', 'Vencimento',
                 'Pagamento', 'R$ Título', 'Valor Pago', 'Desconto', 'Saldo', 'Status'],
        linhas=[[
            str(c.id), c.cliente.nome, c.numero_titulo, c.parcela,
            data(c.emissao), data(c.vencimento), data(c.pagamento),
            numero(c.valor), numero(c.valor_pago), numero(c.desconto),
            numero(c.saldo_devedor), c.get_status_display(),
        ] for c in contas],
    )
    return ExportadorCSV().exportar(dados, 'contas_receber')


@login_required
def baixar_conta(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk, empresa=request.empresa)
    contexto = {'conta': conta, 'formas_pagamento': formas_pagamento()}
    if request.method == 'POST':
        try:
            baixa = FinanceiroFacade().registrar_baixa_receber(conta, request.POST)
        except ValueError as e:
            messages.error(request, str(e))
            contexto['dados'] = request.POST
            return render(request, 'financeiro/baixa.html', contexto)
        messages.success(request, f'Baixa de {formatar_moeda(baixa.valor)} registrada com sucesso!')
        return redirect('financeiro:contas_receber')
    return render(request, 'financeiro/baixa.html', contexto)


@login_required
def contas_pagar(request):
    empresa = request.empresa
    q       = request.GET.get('q', '')
    status  = request.GET.get('status', '')
    contas  = ContaPagar.objects.filter(empresa=empresa)

    hoje = date.today()
    contas.filter(status='pendente', vencimento__lt=hoje).update(status='atrasado')

    if q:
        contas = contas.filter(Q(fornecedor__icontains=q) | Q(descricao__icontains=q))
    if status:
        contas = contas.filter(status=status)

    return render(request, 'financeiro/contas_pagar.html', {
        'contas': contas, 'q': q, 'status': status,
    })


@login_required
def nova_conta_pagar(request):
    if request.method == 'POST':
        try:
            ContaPagar.objects.create(
                empresa=request.empresa,
                fornecedor=request.POST.get('fornecedor'),
                descricao=request.POST.get('descricao'),
                valor=request.POST.get('valor', 0),
                vencimento=request.POST.get('vencimento'),
                categoria=request.POST.get('categoria', ''),
                observacoes=request.POST.get('observacoes', ''),
            )
            messages.success(request, 'Conta a pagar cadastrada!')
            return redirect('financeiro:contas_pagar')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'financeiro/form_conta_pagar.html')


@login_required
def baixas(request):
    empresa = request.empresa
    baixas  = BaixaContaReceber.objects.filter(conta__empresa=empresa).select_related('conta__cliente').order_by('-criado_em')
    return render(request, 'financeiro/baixas.html', {'baixas': baixas})


@login_required
def imprimir_baixa(request, pk):
    baixa = get_object_or_404(BaixaContaReceber, pk=pk, conta__empresa=request.empresa)
    return render(request, 'financeiro/imprimir_baixa.html', {'baixa': baixa})


@login_required
def baixar_conta_pagar(request, pk):
    conta = get_object_or_404(ContaPagar, pk=pk, empresa=request.empresa)
    contexto = {'conta': conta, 'formas_pagamento': formas_pagamento()}
    if request.method == 'POST':
        try:
            baixa = FinanceiroFacade().registrar_baixa_pagar(conta, request.POST)
        except ValueError as e:
            messages.error(request, str(e))
            contexto['dados'] = request.POST
            return render(request, 'financeiro/baixa_pagar.html', contexto)
        messages.success(request, f'Baixa de {formatar_moeda(baixa.valor)} registrada com sucesso!')
        return redirect('financeiro:contas_pagar')
    return render(request, 'financeiro/baixa_pagar.html', contexto)


@login_required
def baixas_pagar(request):
    empresa = request.empresa
    baixas  = BaixaContaPagar.objects.filter(conta__empresa=empresa).select_related('conta').order_by('-criado_em')
    return render(request, 'financeiro/baixas_pagar.html', {'baixas': baixas})
