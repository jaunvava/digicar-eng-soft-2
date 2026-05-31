from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from financeiro.models import ContaReceber
from django.db.models import Sum, Count


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
