from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .models import Cliente, Veiculo



@login_required
def lista(request):
    empresa   = request.empresa
    q_nome    = request.GET.get('q_nome', '').strip()
    q_id      = request.GET.get('q_id',   '').strip()
    q_cpf     = request.GET.get('q_cpf',  '').strip()
    situacao  = request.GET.get('situacao', 'ativo')

    clientes = Cliente.objects.filter(empresa=empresa)

    # Filtro de situação
    if situacao == 'ativo':
        clientes = clientes.filter(ativo=True)
    elif situacao == 'inativo':
        clientes = clientes.filter(ativo=False)
    # 'todos' não filtra

    if q_nome:
        clientes = clientes.filter(nome__icontains=q_nome)
    if q_id:
        try:
            clientes = clientes.filter(pk=int(q_id))
        except ValueError:
            clientes = clientes.none()
    if q_cpf:
        clientes = clientes.filter(cpf_cnpj__icontains=q_cpf)

    total_registros = clientes.count()

    context = {
        'clientes': clientes,
        'total':    total_registros,
        'q_nome':   q_nome,
        'q_id':     q_id,
        'q_cpf':    q_cpf,
        'situacao': situacao,
    }
    return render(request, 'clientes/lista.html', context)


@login_required
def imprimir(request):
    empresa   = request.empresa
    q_nome    = request.GET.get('q_nome', '').strip()
    q_id      = request.GET.get('q_id',   '').strip()
    q_cpf     = request.GET.get('q_cpf',  '').strip()
    situacao  = request.GET.get('situacao', 'ativo')

    clientes = Cliente.objects.filter(empresa=empresa)

    if situacao == 'ativo':
        clientes = clientes.filter(ativo=True)
    elif situacao == 'inativo':
        clientes = clientes.filter(ativo=False)

    if q_nome:
        clientes = clientes.filter(nome__icontains=q_nome)
    if q_id:
        try:
            clientes = clientes.filter(pk=int(q_id))
        except ValueError:
            clientes = clientes.none()
    if q_cpf:
        clientes = clientes.filter(cpf_cnpj__icontains=q_cpf)

    context = {
        'empresa':  empresa,
        'clientes': clientes,
        'total':    clientes.count(),
        'q_nome':   q_nome,
        'q_id':     q_id,
        'q_cpf':    q_cpf,
        'situacao': situacao,
        'now':      timezone.localtime(timezone.now()),
    }
    return render(request, 'clientes/imprimir.html', context)


@login_required
def exportar_excel(request):
    empresa  = request.empresa
    q_nome   = request.GET.get('q_nome', '').strip()
    q_id     = request.GET.get('q_id',   '').strip()
    q_cpf    = request.GET.get('q_cpf',  '').strip()
    situacao = request.GET.get('situacao', 'ativo')

    clientes = Cliente.objects.filter(empresa=empresa)
    if situacao == 'ativo':
        clientes = clientes.filter(ativo=True)
    elif situacao == 'inativo':
        clientes = clientes.filter(ativo=False)
    if q_nome:
        clientes = clientes.filter(nome__icontains=q_nome)
    if q_id:
        try:
            clientes = clientes.filter(pk=int(q_id))
        except ValueError:
            clientes = clientes.none()
    if q_cpf:
        clientes = clientes.filter(cpf_cnpj__icontains=q_cpf)

    # ── Workbook ─────────────────────────────────────────────────────────────
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Clientes'

    # Paleta
    COR_HEADER_FILL = '6366f1'   # roxo (primary do sistema)
    COR_ROW_PAR     = 'f8f7ff'   # lilás muito claro
    COR_ROW_IMPAR   = 'ffffff'
    COR_BORDA       = 'e2e2e2'

    thin = Side(style='thin', color=COR_BORDA)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ── Cabeçalho da empresa (linha 1-2) ─────────────────────────────────────
    ws.merge_cells('A1:H1')
    cell_empresa = ws['A1']
    cell_empresa.value = f"{empresa.nome}  |  CNPJ: {empresa.cnpj or '—'}  |  Tel: {empresa.telefone or '—'}  |  {empresa.email or ''}"
    cell_empresa.font      = Font(bold=True, size=11, color='1e293b')
    cell_empresa.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 22

    ws.merge_cells('A2:H2')
    cell_rel = ws['A2']
    cell_rel.value = f"Relatório de Clientes  —  Gerado em: {timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M:%S')}"
    cell_rel.font      = Font(italic=True, size=9, color='64748b')
    cell_rel.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[2].height = 16

    ws.row_dimensions[3].height = 6  # espaçador

    # ── Cabeçalhos das colunas (linha 4) ─────────────────────────────────────
    headers = ['ID', 'Nome / Razão Social', 'Tipo', 'CPF / CNPJ',
               'E-mail', 'Telefone', 'Cidade', 'UF', 'Status']

    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.font      = Font(bold=True, color='ffffff', size=10)
        cell.fill      = PatternFill('solid', fgColor=COR_HEADER_FILL)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border    = border
    ws.row_dimensions[4].height = 20

    # ── Dados ─────────────────────────────────────────────────────────────────
    for row_idx, c in enumerate(clientes, start=5):
        fill_color = COR_ROW_PAR if row_idx % 2 == 0 else COR_ROW_IMPAR
        row_fill   = PatternFill('solid', fgColor=fill_color)

        values = [
            c.pk,
            c.nome,
            c.get_tipo_display(),
            c.cpf_cnpj or '',
            c.email or '',
            c.telefone or c.celular or '',
            c.cidade or '',
            c.estado or '',
            'Ativo' if c.ativo else 'Inativo',
        ]
        for col_idx, value in enumerate(values, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.fill      = row_fill
            cell.border    = border
            cell.alignment = Alignment(vertical='center')
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            if col_idx == 9:  # Status
                cell.font = Font(
                    bold=True,
                    color='065f46' if c.ativo else '991b1b'
                )
        ws.row_dimensions[row_idx].height = 16

    # ── Larguras automáticas ──────────────────────────────────────────────────
    col_widths = [7, 38, 14, 20, 32, 16, 20, 6, 10]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Congela cabeçalho
    ws.freeze_panes = 'A5'

    # ── Resposta HTTP ─────────────────────────────────────────────────────────
    from io import BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = f"clientes_{timezone.localtime(timezone.now()).strftime('%Y%m%d_%H%M')}.xlsx"
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required

def novo(request):
    if request.method == 'POST':
        try:
            Cliente.objects.create(
                empresa=request.empresa,
                ativo=(request.POST.get('ativo') == 'on'),
                tipo=request.POST.get('tipo', 'PF'),
                nome=request.POST.get('nome'),
                cpf_cnpj=request.POST.get('cpf_cnpj', ''),
                email=request.POST.get('email', ''),
                telefone=request.POST.get('telefone', ''),
                celular=request.POST.get('celular', ''),
                cep=request.POST.get('cep', ''),
                endereco=request.POST.get('endereco', ''),
                numero=request.POST.get('numero', ''),
                complemento=request.POST.get('complemento', ''),
                bairro=request.POST.get('bairro', ''),
                cidade=request.POST.get('cidade', ''),
                estado=request.POST.get('estado', ''),
                observacoes=request.POST.get('observacoes', ''),
            )
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('clientes:lista')
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar cliente: {e}')
    return render(request, 'clientes/form.html', {'titulo': 'Novo Cliente', 'action': 'novo'})


@login_required
def editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        try:
            cliente.ativo       = (request.POST.get('ativo') == 'on')
            cliente.tipo        = request.POST.get('tipo', 'PF')
            cliente.nome        = request.POST.get('nome')
            cliente.cpf_cnpj   = request.POST.get('cpf_cnpj', '')
            cliente.email       = request.POST.get('email', '')
            cliente.telefone    = request.POST.get('telefone', '')
            cliente.celular     = request.POST.get('celular', '')
            cliente.cep         = request.POST.get('cep', '')
            cliente.endereco    = request.POST.get('endereco', '')
            cliente.numero      = request.POST.get('numero', '')
            cliente.complemento = request.POST.get('complemento', '')
            cliente.bairro      = request.POST.get('bairro', '')
            cliente.cidade      = request.POST.get('cidade', '')
            cliente.estado      = request.POST.get('estado', '')
            cliente.observacoes = request.POST.get('observacoes', '')
            cliente.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('clientes:lista')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {e}')
    return render(request, 'clientes/form.html', {'titulo': 'Editar Cliente', 'cliente': cliente, 'action': 'editar'})


@login_required
def excluir(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk, empresa=request.empresa)
    cliente.delete()
    messages.success(request, 'Cliente excluído com sucesso!')
    return redirect('clientes:lista')


@login_required
def detalhe(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk, empresa=request.empresa)
    return render(request, 'clientes/detalhe.html', {'cliente': cliente, 'veiculos': cliente.veiculos.filter(ativo=True)})


@login_required
def veiculos(request):
    qs = Veiculo.objects.filter(cliente__empresa=request.empresa).select_related('cliente')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(placa__icontains=q) | Q(modelo__icontains=q) | Q(cliente__nome__icontains=q))
    return render(request, 'clientes/veiculos.html', {'veiculos': qs, 'q': q})


@login_required
def novo_veiculo(request):
    clientes = Cliente.objects.filter(empresa=request.empresa, ativo=True)
    if request.method == 'POST':
        try:
            Veiculo.objects.create(
                cliente=get_object_or_404(clientes, pk=request.POST.get('cliente')),
                placa=request.POST.get('placa', '').strip().upper(),
                marca=request.POST.get('marca', '').strip(), modelo=request.POST.get('modelo', '').strip(),
                ano=request.POST.get('ano') or None, cor=request.POST.get('cor', '').strip(),
                chassi=request.POST.get('chassi', '').strip(), observacoes=request.POST.get('observacoes', '').strip(),
            )
            messages.success(request, 'Veículo cadastrado com sucesso!')
            return redirect('clientes:veiculos')
        except Exception as exc:
            messages.error(request, f'Erro ao cadastrar veículo: {exc}')
    return render(request, 'clientes/veiculo_form.html', {'clientes': clientes, 'titulo': 'Novo Veículo'})


@login_required
def editar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk, cliente__empresa=request.empresa)
    clientes = Cliente.objects.filter(empresa=request.empresa, ativo=True)
    if request.method == 'POST':
        veiculo.cliente = get_object_or_404(clientes, pk=request.POST.get('cliente'))
        veiculo.placa = request.POST.get('placa', '').strip().upper()
        veiculo.marca = request.POST.get('marca', '').strip(); veiculo.modelo = request.POST.get('modelo', '').strip()
        veiculo.ano = request.POST.get('ano') or None; veiculo.cor = request.POST.get('cor', '').strip()
        veiculo.chassi = request.POST.get('chassi', '').strip(); veiculo.observacoes = request.POST.get('observacoes', '').strip()
        veiculo.save()
        messages.success(request, 'Veículo atualizado!')
        return redirect('clientes:veiculos')
    return render(request, 'clientes/veiculo_form.html', {'clientes': clientes, 'veiculo': veiculo, 'titulo': 'Editar Veículo'})


@login_required
def excluir_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk, cliente__empresa=request.empresa)
    veiculo.delete()
    messages.success(request, 'Veículo excluído!')
    return redirect('clientes:veiculos')


@login_required
def detalhe_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk, cliente__empresa=request.empresa)
    return render(request, 'clientes/veiculo_detalhe.html', {'veiculo': veiculo, 'ordens': veiculo.ordens_servico.select_related('cliente')})
