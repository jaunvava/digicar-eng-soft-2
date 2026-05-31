from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Orcamento, ItemOrcamento
from clientes.models import Cliente
from produtos.models import Produto


@login_required
def lista(request):
    empresa   = request.empresa
    q         = request.GET.get('q', '')
    status    = request.GET.get('status', '')
    orcamentos = Orcamento.objects.filter(empresa=empresa).select_related('cliente')
    if q:
        orcamentos = orcamentos.filter(Q(numero__icontains=q) | Q(cliente__nome__icontains=q))
    if status:
        orcamentos = orcamentos.filter(status=status)
    return render(request, 'orcamentos/lista.html', {'orcamentos': orcamentos, 'q': q, 'status': status})


@login_required
def novo(request):
    empresa  = request.empresa
    clientes = Cliente.objects.filter(empresa=empresa, ativo=True)
    produtos = Produto.objects.filter(empresa=empresa, ativo=True)
    if request.method == 'POST':
        try:
            orc = Orcamento.objects.create(
                empresa=empresa,
                cliente_id=request.POST.get('cliente'),
                vendedor=request.user,
                validade=request.POST.get('validade'),
                desconto=request.POST.get('desconto', 0) or 0,
                observacoes=request.POST.get('observacoes', ''),
            )
            # Itens via POST múltiplos
            produtos_ids   = request.POST.getlist('produto_id')
            quantidades    = request.POST.getlist('quantidade')
            precos         = request.POST.getlist('preco_unitario')
            subtotal_total = 0
            for pid, qty, preco in zip(produtos_ids, quantidades, precos):
                if not pid: continue
                qty   = float(qty or 1)
                preco = float(preco or 0)
                item = ItemOrcamento.objects.create(
                    orcamento=orc, produto_id=pid,
                    quantidade=qty, preco_unitario=preco, subtotal=qty*preco
                )
                subtotal_total += item.subtotal
            orc.subtotal = subtotal_total
            orc.total    = subtotal_total - float(orc.desconto)
            orc.save()
            messages.success(request, f'Orçamento #{orc.numero} criado!')
            return redirect('orcamentos:lista')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'orcamentos/form.html', {
        'titulo': 'Novo Orçamento', 'clientes': clientes, 'produtos': produtos
    })


@login_required
def detalhe(request, pk):
    orc   = get_object_or_404(Orcamento, pk=pk, empresa=request.empresa)
    itens = orc.itens.select_related('produto')
    return render(request, 'orcamentos/detalhe.html', {'orcamento': orc, 'itens': itens})


@login_required
def alterar_status(request, pk):
    orc = get_object_or_404(Orcamento, pk=pk, empresa=request.empresa)
    novo_status = request.POST.get('status')
    if novo_status in dict(Orcamento.STATUS_CHOICES):
        orc.status = novo_status
        orc.save()
        messages.success(request, f'Status atualizado para {orc.get_status_display()}')
    return redirect('orcamentos:detalhe', pk=pk)


@login_required
def imprimir(request, pk):
    orc = get_object_or_404(Orcamento, pk=pk, empresa=request.empresa)
    itens = orc.itens.select_related('produto')
    return render(request, 'orcamentos/imprimir.html', {'orcamento': orc, 'itens': itens})
