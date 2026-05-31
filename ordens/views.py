from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import OrdemServico, ItemOrdemServico
from clientes.models import Cliente
from produtos.models import Produto
from django.contrib.auth.models import User


@login_required
def lista(request):
    empresa = request.empresa
    q       = request.GET.get('q', '')
    status  = request.GET.get('status', '')
    ordens  = OrdemServico.objects.filter(empresa=empresa).select_related('cliente', 'tecnico')
    if q:
        ordens = ordens.filter(
            Q(numero__icontains=q) | Q(cliente__nome__icontains=q) | Q(equipamento__icontains=q)
        )
    if status:
        ordens = ordens.filter(status=status)
    return render(request, 'ordens/lista.html', {
        'ordens': ordens, 'q': q, 'status': status,
        'status_choices': OrdemServico.STATUS_CHOICES,
    })


@login_required
def nova(request):
    empresa  = request.empresa
    clientes = Cliente.objects.filter(empresa=empresa, ativo=True)
    produtos = Produto.objects.filter(empresa=empresa, ativo=True)
    tecnicos = User.objects.filter(perfil__empresa=empresa, perfil__ativo=True)
    if request.method == 'POST':
        try:
            from decimal import Decimal

            tecnico_id    = request.POST.get('tecnico') or None
            data_prevista = request.POST.get('data_prevista') or None
            desconto      = Decimal(str(request.POST.get('desconto', '0') or '0'))
            garantia      = int(request.POST.get('garantia_dias', '30') or '30')

            os = OrdemServico.objects.create(
                empresa=empresa,
                cliente_id=request.POST.get('cliente'),
                tecnico_id=tecnico_id,
                status=request.POST.get('status', 'aberta'),
                prioridade=request.POST.get('prioridade', 'normal'),
                equipamento=request.POST.get('equipamento'),
                marca=request.POST.get('marca', ''),
                modelo=request.POST.get('modelo', ''),
                numero_serie=request.POST.get('numero_serie', ''),
                defeito_reclamado=request.POST.get('defeito_reclamado'),
                defeito_constatado=request.POST.get('defeito_constatado', ''),
                solucao=request.POST.get('solucao', ''),
                data_prevista=data_prevista,
                desconto=desconto,
                observacoes=request.POST.get('observacoes', ''),
                garantia_dias=garantia,
                # zera os valores; serão recalculados abaixo
                valor_servicos=Decimal('0'),
                valor_pecas=Decimal('0'),
            )

            # Itens
            tipos      = request.POST.getlist('item_tipo')
            descricoes = request.POST.getlist('item_descricao')
            qtds       = request.POST.getlist('item_quantidade')
            precos     = request.POST.getlist('item_preco')

            v_servicos = Decimal('0')
            v_pecas    = Decimal('0')

            for tipo, desc, qty, preco in zip(tipos, descricoes, qtds, precos):
                if not desc.strip():
                    continue
                qty   = Decimal(str(qty  or '1'))
                preco = Decimal(str(preco or '0'))
                item  = ItemOrdemServico.objects.create(
                    ordem=os, tipo=tipo, descricao=desc,
                    quantidade=qty, preco_unitario=preco, subtotal=qty * preco,
                )
                if tipo == 'servico':
                    v_servicos += item.subtotal
                else:
                    v_pecas += item.subtotal

            os.valor_servicos = v_servicos
            os.valor_pecas    = v_pecas
            os.save()  # total = v_servicos + v_pecas - desconto (tudo Decimal)

            messages.success(request, f'OS #{os.numero} criada com sucesso!')
            return redirect('ordens:detalhe', pk=os.pk)
        except Exception as e:
            messages.error(request, f'Erro ao criar OS: {e}')
    return render(request, 'ordens/form.html', {
        'titulo': 'Nova Ordem de Serviço',
        'clientes': clientes, 'produtos': produtos, 'tecnicos': tecnicos,
        'status_choices': OrdemServico.STATUS_CHOICES,
        'prioridade_choices': OrdemServico.PRIORIDADE_CHOICES,
    })


@login_required
def detalhe(request, pk):
    os    = get_object_or_404(OrdemServico, pk=pk, empresa=request.empresa)
    itens = os.itens.all()
    return render(request, 'ordens/detalhe.html', {'os': os, 'itens': itens})


@login_required
def editar_status(request, pk):
    os = get_object_or_404(OrdemServico, pk=pk, empresa=request.empresa)
    novo_status = request.POST.get('status')
    if novo_status in dict(OrdemServico.STATUS_CHOICES):
        os.status = novo_status
        if novo_status in ('pronta', 'entregue'):
            os.data_conclusao = timezone.now()
        os.save()
        messages.success(request, f'Status atualizado: {os.get_status_display()}')
    return redirect('ordens:detalhe', pk=pk)


@login_required
def excluir(request, pk):
    os = get_object_or_404(OrdemServico, pk=pk, empresa=request.empresa)
    os.delete()
    messages.success(request, 'OS excluída.')
    return redirect('ordens:lista')


@login_required
def imprimir(request, pk):
    os = get_object_or_404(OrdemServico, pk=pk, empresa=request.empresa)
    itens = os.itens.select_related('produto')
    return render(request, 'ordens/imprimir.html', {'os': os, 'itens': itens})
