from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Produto
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


@login_required
def lista(request):
    empresa = request.empresa
    q    = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    situacao = request.GET.get('situacao', 'ativo')
    produtos = Produto.objects.filter(empresa=empresa)
    
    if situacao == 'ativo':
        produtos = produtos.filter(ativo=True)
    elif situacao == 'inativo':
        produtos = produtos.filter(ativo=False)

    if q:
        produtos = produtos.filter(Q(nome__icontains=q) | Q(codigo__icontains=q))
    if tipo:
        produtos = produtos.filter(tipo=tipo)

    total_registros = produtos.count()

    per_page = request.GET.get('per_page', '20')
    if per_page not in ['20', '50', '100']:
        per_page = '20'

    paginator = Paginator(produtos, int(per_page))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'produtos': page_obj,
        'page_obj': page_obj,
        'q': q,
        'tipo': tipo,
        'situacao': situacao,
        'total': total_registros,
        'per_page': per_page,
    }
    return render(request, 'produtos/lista.html', context)
    
@login_required
def imprimir(request):
    empresa = request.empresa
    q    = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    situacao = request.GET.get('situacao', 'ativo')
    produtos = Produto.objects.filter(empresa=empresa)
    
    if situacao == 'ativo':
        produtos = produtos.filter(ativo=True)
    elif situacao == 'inativo':
        produtos = produtos.filter(ativo=False)

    if q:
        produtos = produtos.filter(Q(nome__icontains=q) | Q(codigo__icontains=q))
    if tipo:
        produtos = produtos.filter(tipo=tipo)
        
    context = {
        'empresa':  empresa,
        'produtos': produtos,
        'total':    produtos.count(),
        'q':        q,
        'tipo':     tipo,
        'situacao': situacao,
        'now':      timezone.localtime(timezone.now()),
    }
    return render(request, 'produtos/imprimir.html', context)

from django.http import HttpResponse

@login_required
def exportar_excel(request):
    empresa = request.empresa
    q    = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    situacao = request.GET.get('situacao', 'ativo')
    produtos = Produto.objects.filter(empresa=empresa)
    
    if situacao == 'ativo':
        produtos = produtos.filter(ativo=True)
    elif situacao == 'inativo':
        produtos = produtos.filter(ativo=False)

    if q:
        produtos = produtos.filter(Q(nome__icontains=q) | Q(codigo__icontains=q))
    if tipo:
        produtos = produtos.filter(tipo=tipo)

    # ── Workbook ─────────────────────────────────────────────────────────────
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Produtos'

    COR_HEADER_FILL = '6366f1'
    COR_ROW_PAR     = 'f8f7ff'
    COR_ROW_IMPAR   = 'ffffff'
    COR_BORDA       = 'e2e2e2'

    thin = Side(style='thin', color=COR_BORDA)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # Cabeçalho da empresa (linha 1-2)
    ws.merge_cells('A1:G1')
    cell_empresa = ws['A1']
    cell_empresa.value = f"{empresa.nome}  |  CNPJ: {empresa.cnpj or '—'}  |  Tel: {empresa.telefone or '—'}  |  {empresa.email or ''}"
    cell_empresa.font      = Font(bold=True, size=11, color='1e293b')
    cell_empresa.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 22

    ws.merge_cells('A2:G2')
    cell_rel = ws['A2']
    cell_rel.value = f"Relatório de Produtos  —  Gerado em: {timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M:%S')}"
    cell_rel.font      = Font(italic=True, size=9, color='64748b')
    cell_rel.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[2].height = 16

    ws.row_dimensions[3].height = 6

    # ── Cabeçalhos das colunas (linha 4)
    headers = ['Código', 'Nome do Produto/Serviço', 'Tipo', 'Preço Custo', 'Preço Venda', 'Estoque']
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.font      = Font(bold=True, color='ffffff', size=10)
        cell.fill      = PatternFill('solid', fgColor=COR_HEADER_FILL)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border    = border
    ws.row_dimensions[4].height = 20

    # ── Dados ─────────────────────────────────────────────────────────────────
    for row_idx, p in enumerate(produtos, start=5):
        fill_color = COR_ROW_PAR if row_idx % 2 == 0 else COR_ROW_IMPAR
        row_fill   = PatternFill('solid', fgColor=fill_color)

        dados_linha = [
            p.codigo or '-',
            p.nome,
            p.get_tipo_display(),
            float(p.preco_custo),
            float(p.preco_venda),
            float(p.estoque_atual) if p.tipo == 'produto' else '-'
        ]
        
        for col_idx, valor in enumerate(dados_linha, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=valor)
            cell.fill = row_fill
            cell.border = border
            cell.alignment = Alignment(vertical='center')
            if col_idx in (5, 6):
                cell.number_format = 'R$ #,##0.00'

    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 15

    ws.freeze_panes = 'A5'

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="produtos.xlsx"'
    wb.save(response)
    return response


@login_required
def novo(request):
    empresa = request.empresa
    if request.method == 'POST':
        try:
            Produto.objects.create(
                empresa=empresa,
                ativo=(request.POST.get('ativo') in ['on', 'True', 'true', '1']),
                tipo=request.POST.get('tipo', 'produto'),
                codigo=request.POST.get('codigo', ''),
                nome=request.POST.get('nome'),
                unidade=request.POST.get('unidade', 'UN'),
                preco_custo=request.POST.get('preco_custo', 0) or 0,
                preco_venda=request.POST.get('preco_venda', 0) or 0,
                estoque_atual=request.POST.get('estoque_atual', 0) or 0,
                estoque_minimo=request.POST.get('estoque_minimo', 0) or 0,
            )
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produtos:lista')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'produtos/form.html', {'titulo': 'Novo Produto'})


@login_required
def editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        try:
            produto.ativo         = (request.POST.get('ativo') in ['on', 'True', 'true', '1'])
            produto.tipo          = request.POST.get('tipo', 'produto')
            produto.codigo        = request.POST.get('codigo', '')
            produto.nome          = request.POST.get('nome')
            produto.unidade       = request.POST.get('unidade', 'UN')
            produto.preco_custo   = request.POST.get('preco_custo', 0) or 0
            produto.preco_venda   = request.POST.get('preco_venda', 0) or 0
            produto.estoque_atual = request.POST.get('estoque_atual', 0) or 0
            produto.estoque_minimo = request.POST.get('estoque_minimo', 0) or 0
            produto.save()
            messages.success(request, 'Produto atualizado!')
            return redirect('produtos:lista')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'produtos/form.html', {'titulo': 'Editar Produto', 'produto': produto})


@login_required
def excluir(request, pk):
    produto = get_object_or_404(Produto, pk=pk, empresa=request.empresa)
    produto.delete()
    messages.success(request, 'Produto excluído!')
    return redirect('produtos:lista')
