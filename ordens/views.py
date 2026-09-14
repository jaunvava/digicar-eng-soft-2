from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from .models import OrdemServico, ItemOrdemServico
from clientes.models import Cliente, Veiculo
from produtos.models import Produto, MovimentoEstoque
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
    veiculos = Veiculo.objects.filter(cliente__empresa=empresa, ativo=True).select_related('cliente')
    produtos = Produto.objects.filter(empresa=empresa, ativo=True)
    tecnicos = User.objects.filter(perfil__empresa=empresa, perfil__ativo=True)
    if request.method == 'POST':
        try:
            tecnico_id    = request.POST.get('tecnico') or None
            data_prevista = request.POST.get('data_prevista') or None
            desconto      = Decimal(str(request.POST.get('desconto', '0') or '0'))
            garantia      = int(request.POST.get('garantia_dias', '30') or '30')

            cliente = get_object_or_404(clientes, pk=request.POST.get('cliente'))
            veiculo = None
            if request.POST.get('veiculo'):
                veiculo = get_object_or_404(Veiculo, pk=request.POST.get('veiculo'), cliente=cliente)

            tecnico = get_object_or_404(tecnicos, pk=tecnico_id) if tecnico_id else None
            tipos = request.POST.getlist('item_tipo')
            produtos_ids = request.POST.getlist('item_produto')
            descricoes = request.POST.getlist('item_descricao')
            qtds = request.POST.getlist('item_quantidade')
            precos = request.POST.getlist('item_preco')

            with transaction.atomic():
                os = OrdemServico.objects.create(
                    empresa=empresa, cliente=cliente, veiculo=veiculo, tecnico=tecnico,
                    status=request.POST.get('status', 'aberta'),
                    prioridade=request.POST.get('prioridade', 'normal'),
                    equipamento=request.POST.get('equipamento'), marca=request.POST.get('marca', ''),
                    modelo=request.POST.get('modelo', ''), numero_serie=request.POST.get('numero_serie', ''),
                    defeito_reclamado=request.POST.get('defeito_reclamado'),
                    defeito_constatado=request.POST.get('defeito_constatado', ''),
                    solucao=request.POST.get('solucao', ''), data_prevista=data_prevista,
                    desconto=desconto, observacoes=request.POST.get('observacoes', ''),
                    garantia_dias=garantia, valor_servicos=Decimal('0'), valor_pecas=Decimal('0'),
                )

                v_servicos = Decimal('0')
                v_pecas = Decimal('0')
                total_itens = max(len(tipos), len(produtos_ids), len(descricoes), len(qtds), len(precos))
                for indice in range(total_itens):
                    tipo = tipos[indice] if indice < len(tipos) else 'servico'
                    produto_id = produtos_ids[indice] if indice < len(produtos_ids) else ''
                    desc = descricoes[indice].strip() if indice < len(descricoes) else ''
                    qty = Decimal(str(qtds[indice] or '1')) if indice < len(qtds) else Decimal('1')
                    preco = Decimal(str(precos[indice] or '0')) if indice < len(precos) else Decimal('0')
                    if qty <= 0 or preco < 0:
                        raise ValueError('Quantidade e preço dos itens devem ser válidos.')

                    produto = None
                    if produto_id:
                        produto = Produto.objects.select_for_update().get(pk=produto_id, empresa=empresa, ativo=True)
                        tipo = 'peca' if produto.tipo == 'produto' else 'servico'
                        desc = desc or produto.nome
                        if tipo == 'peca':
                            if produto.estoque_atual < qty:
                                raise ValueError(f'Estoque insuficiente para {produto.nome}. Disponível: {produto.estoque_atual}.')
                            anterior = produto.estoque_atual
                            produto.estoque_atual -= qty
                            produto.save(update_fields=['estoque_atual', 'atualizado_em'])
                            MovimentoEstoque.objects.create(
                                produto=produto, tipo='saida', quantidade=qty,
                                estoque_anterior=anterior, estoque_posterior=produto.estoque_atual,
                                motivo=f'Utilização na OS #{os.numero}', usuario=request.user,
                            )
                    if not desc:
                        continue
                    item = ItemOrdemServico.objects.create(
                        ordem=os, tipo=tipo, produto=produto, descricao=desc,
                        quantidade=qty, preco_unitario=preco, subtotal=qty * preco,
                    )
                    if tipo == 'servico': v_servicos += item.subtotal
                    else: v_pecas += item.subtotal

                os.valor_servicos = v_servicos
                os.valor_pecas = v_pecas
                os.save()

            messages.success(request, f'OS #{os.numero} criada com sucesso!')
            return redirect('ordens:detalhe', pk=os.pk)
        except (InvalidOperation, ValueError, Produto.DoesNotExist) as e:
            messages.error(request, f'Erro ao criar OS: {e}')
    return render(request, 'ordens/form.html', {
        'titulo': 'Nova Ordem de Serviço',
        'clientes': clientes, 'veiculos': veiculos, 'produtos': produtos, 'tecnicos': tecnicos,
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
    with transaction.atomic():
        for item in os.itens.filter(tipo='peca', produto__isnull=False).select_related('produto'):
            produto = Produto.objects.select_for_update().get(pk=item.produto_id)
            anterior = produto.estoque_atual
            produto.estoque_atual += item.quantidade
            produto.save(update_fields=['estoque_atual', 'atualizado_em'])
            MovimentoEstoque.objects.create(
                produto=produto, tipo='entrada', quantidade=item.quantidade,
                estoque_anterior=anterior, estoque_posterior=produto.estoque_atual,
                motivo=f'Estorno por exclusão da OS #{os.numero}', usuario=request.user,
            )
        os.delete()
    messages.success(request, 'OS excluída.')
    return redirect('ordens:lista')


@login_required
def imprimir(request, pk):
    os = get_object_or_404(OrdemServico, pk=pk, empresa=request.empresa)
    itens = os.itens.select_related('produto')
    return render(request, 'ordens/imprimir.html', {'os': os, 'itens': itens})
