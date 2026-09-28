from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, F
from datetime import timedelta, date
import json

from core.models import Empresa, PerfilUsuario



def login_view(request):
    if request.user.is_authenticated:
        if getattr(request, 'empresa', None):
            return redirect('core:dashboard')
        logout(request)
        messages.warning(request, 'Seu usuário está autenticado, mas não está vinculado a uma empresa. Faça login novamente.')
        return render(request, 'core/login.html')

    if request.method == 'POST':
        codigo_empresa = request.POST.get('codigo_empresa', '').strip().upper()
        username       = request.POST.get('username', '').strip()
        password       = request.POST.get('password', '')

        try:
            empresa = Empresa.objects.get(codigo=codigo_empresa, ativo=True)
        except Empresa.DoesNotExist:
            messages.error(request, 'CÃ³digo de empresa invÃ¡lido ou empresa inativa.')
            return render(request, 'core/login.html')

        # Campo removido â€” nenhuma restriÃ§Ã£o de acesso web por empresa aqui

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'UsuÃ¡rio ou senha incorretos.')
            return render(request, 'core/login.html')

        # Verifica vÃ­nculo com empresa
        try:
            perfil = user.perfil
            if perfil.empresa != empresa:
                messages.error(request, 'UsuÃ¡rio nÃ£o pertence a esta empresa.')
                return render(request, 'core/login.html')
            if not perfil.ativo:
                messages.error(request, 'UsuÃ¡rio inativo. Contate o administrador.')
                return render(request, 'core/login.html')
        except PerfilUsuario.DoesNotExist:
            messages.error(request, 'Perfil de usuÃ¡rio nÃ£o configurado.')
            return render(request, 'core/login.html')

        login(request, user)
        return redirect('core:dashboard')

    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('core:login')


@login_required
def dashboard(request):
    empresa = request.empresa
    if not empresa:
        logout(request)
        messages.error(request, 'Não foi possível identificar a empresa do usuário. Faça login novamente.')
        return redirect('core:login')

    from clientes.models import Cliente
    from produtos.models import Produto
    from financeiro.models import ContaReceber
    from ordens.models import OrdemServico

    hoje = date.today()
    ini_mes = hoje.replace(day=1)

    # Stats
    total_clientes  = Cliente.objects.filter(empresa=empresa, ativo=True).count()
    clientes_mes    = Cliente.objects.filter(empresa=empresa, criado_em__date__gte=ini_mes).count()
    total_produtos  = Produto.objects.filter(empresa=empresa, ativo=True).count()
    total_devedor   = ContaReceber.objects.filter(empresa=empresa, status__in=['pendente','atrasado']).aggregate(t=Sum('valor'))['t'] or 0

    # Status recebimentos
    rec_atrasado = float(ContaReceber.objects.filter(empresa=empresa, status='atrasado').aggregate(t=Sum('valor'))['t'] or 0)
    rec_pago     = float(ContaReceber.objects.filter(empresa=empresa, status='pago').aggregate(t=Sum('valor'))['t'] or 0)
    rec_pendente = float(ContaReceber.objects.filter(empresa=empresa, status='pendente').aggregate(t=Sum('valor'))['t'] or 0)

    # Ãšltimas OS
    ultimas_os = OrdemServico.objects.filter(empresa=empresa).order_by('-data_entrada')[:8]

    # Contas atrasadas
    contas_atrasadas = ContaReceber.objects.filter(
        empresa=empresa, status='atrasado'
    ).order_by('-valor')[:10]

    # Banners
    from core.models import BannerDashboard
    banners = BannerDashboard.objects.filter(ativo=True)

    context = {
        'total_clientes': total_clientes,
        'clientes_mes': clientes_mes,
        'total_produtos': total_produtos,
        'total_devedor': total_devedor,
        'rec_atrasado': rec_atrasado,
        'rec_pago': rec_pago,
        'rec_pendente': rec_pendente,
        'ultimas_os': ultimas_os,
        'contas_atrasadas': contas_atrasadas,
        'banners': banners,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def perfil_view(request):
    # Verifica se é uma requisição POST (edição)
    if request.method == 'POST':
        print("=== POST recebido em perfil_view ===")
        print(f"POST data: {request.POST}")
        
        # Verifica se é o formulário de edição
        if 'edit_perfil' in request.POST:
            try:
                # 1. Atualiza dados do User
                user = request.user
                user.first_name = request.POST.get('first_name', '').strip()
                user.last_name = request.POST.get('last_name', '').strip()
                user.email = request.POST.get('email', '').strip()
                user.save()
                print(f"User atualizado: {user.username}")
                
                # 2. Atualiza dados do Perfil
                perfil = request.user.perfil
                perfil.telefone = request.POST.get('telefone', '').strip()
                perfil.celular = request.POST.get('celular', '').strip()
                perfil.cargo = request.POST.get('cargo', '').strip()
                
                # Data de nascimento - tratamento especial
                data_nascimento = request.POST.get('data_nascimento', '')
                if data_nascimento:
                    from datetime import datetime
                    try:
                        perfil.data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
                        print(f"Data nascimento: {perfil.data_nascimento}")
                    except Exception as e:
                        print(f"Erro na data: {e}")
                
                perfil.save()
                print(f"Perfil atualizado com sucesso!")
                
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('core:perfil')
                
            except Exception as e:
                print(f"ERRO ao salvar: {str(e)}")
                messages.error(request, f'Erro ao salvar: {str(e)}')
                return redirect('core:perfil')
        else:
            print("WARNING: POST sem edit_perfil no payload")
    
    # GET request - apenas mostra o formulário
    return render(request, 'core/perfil.html')


@login_required
def notificacoes_json(request):
    """Retorna notificaÃ§Ãµes reais em JSON para o sino da navbar."""
    from django.http import JsonResponse
    from financeiro.models import ContaReceber, ContaPagar
    from ordens.models import OrdemServico
    from produtos.models import Produto

    empresa = request.empresa
    notifs  = []
    hoje    = date.today()

    # â”€â”€ OS urgentes abertas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    os_urgentes = OrdemServico.objects.filter(
        empresa=empresa,
        prioridade='urgente',
        status__in=['aberta', 'em_andamento']
    ).order_by('-data_entrada')[:5]
    for os in os_urgentes:
        notifs.append({
            'tipo': 'urgente',
            'icone': 'bi-tools',
            'titulo': f'OS Urgente #{os.numero}',
            'descricao': f'{os.cliente.nome} â€” {os.equipamento}',
            'url': f'/ordens/{os.pk}/',
            'cor': '#ef4444',
        })

    # â”€â”€ OS aguardando hÃ¡ mais de 7 dias â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    limite_espera = hoje - timedelta(days=7)
    os_atrasadas = OrdemServico.objects.filter(
        empresa=empresa,
        status__in=['aberta', 'em_andamento'],
        data_entrada__date__lte=limite_espera,
    ).exclude(prioridade='urgente').order_by('data_entrada')[:3]
    for os in os_atrasadas:
        dias = (hoje - os.data_entrada.date()).days
        notifs.append({
            'tipo': 'aviso',
            'icone': 'bi-clock-history',
            'titulo': f'OS #{os.numero} aguardando {dias}d',
            'descricao': f'{os.cliente.nome} â€” {os.get_status_display()}',
            'url': f'/ordens/{os.pk}/',
            'cor': '#f59e0b',
        })

    # â”€â”€ Contas a receber atrasadas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    cr_atrasadas = ContaReceber.objects.filter(
        empresa=empresa,
        status='atrasado'
    ).order_by('vencimento')[:5]
    for cr in cr_atrasadas:
        notifs.append({
            'tipo': 'perigo',
            'icone': 'bi-cash-stack',
            'titulo': f'Receber atrasado: R$ {cr.valor:.2f}',
            'descricao': f'{cr.cliente.nome} â€” venceu {cr.vencimento.strftime("%d/%m/%Y")}',
            'url': '/financeiro/receber/',
            'cor': '#ef4444',
        })

    # â”€â”€ Contas a pagar vencendo hoje ou atrasadas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    cp_vencendo = ContaPagar.objects.filter(
        empresa=empresa,
        status__in=['pendente', 'atrasado'],
        vencimento__lte=hoje
    ).order_by('vencimento')[:5]
    for cp in cp_vencendo:
        vencida = cp.vencimento < hoje
        notifs.append({
            'tipo': 'perigo' if vencida else 'aviso',
            'icone': 'bi-arrow-up-circle',
            'titulo': f'Pagar {"atrasado" if vencida else "hoje"}: R$ {cp.valor:.2f}',
            'descricao': f'{cp.fornecedor} â€” {cp.descricao[:40]}',
            'url': '/financeiro/pagar/',
            'cor': '#ef4444' if vencida else '#f59e0b',
        })

    # â”€â”€ Produtos com estoque baixo â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    estoques_baixos = Produto.objects.filter(
        empresa=empresa,
        tipo='produto',
        ativo=True,
        estoque_atual__lte=F('estoque_minimo'),
    ).exclude(estoque_minimo=0)[:5]
    for p in estoques_baixos:
        notifs.append({
            'tipo': 'info',
            'icone': 'bi-box-seam',
            'titulo': f'Estoque baixo: {p.nome}',
            'descricao': f'{float(p.estoque_atual):.0f} {p.unidade} (mÃ­n: {float(p.estoque_minimo):.0f})',
            'url': '/produtos/',
            'cor': '#f59e0b',
        })

    return JsonResponse({'total': len(notifs), 'items': notifs})


@login_required
def configuracoes_view(request):
    empresa = request.empresa
    if not empresa:
        return redirect('core:login')
    
    from core.models import ConfiguracaoEmpresa, PerfilUsuario
    config, created = ConfiguracaoEmpresa.objects.get_or_create(empresa=empresa)
    
    if request.method == 'POST' and 'update_config' in request.POST:
        config.whatsapp_notificacao = 'whatsapp_notificacao' in request.POST
        config.impressao_automatica_pdv = 'impressao_automatica_pdv' in request.POST
        config.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'sucesso': True})
        messages.success(request, 'ConfiguraÃ§Ãµes de sistema atualizadas com sucesso!')
        return redirect('core:configuracoes')

    usuarios = PerfilUsuario.objects.filter(empresa=empresa).select_related('user')
    
    context = {
        'empresa': empresa,
        'config': config,
        'usuarios': usuarios,
    }
    return render(request, 'core/configuracoes.html', context)


@login_required
def aplicativos_view(request):
    empresa = request.empresa
    if not empresa:
        return redirect('core:login')
    
    context = {}
    return render(request, 'core/aplicativos.html', context)

