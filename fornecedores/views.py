from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Fornecedor

@login_required
def lista(request):
    empresa = request.empresa
    q = request.GET.get('q', '')
    fornecedores = Fornecedor.objects.filter(empresa=empresa)
    
    if q:
        fornecedores = fornecedores.filter(
            Q(nome__icontains=q) | 
            Q(cpf_cnpj__icontains=q) |
            Q(email__icontains=q)
        )
    
    context = {
        'fornecedores': fornecedores,
        'q': q,
        'total': fornecedores.count(),
    }
    return render(request, 'fornecedores/lista.html', context)

@login_required
def novo(request):
    if request.method == 'POST':
        try:
            Fornecedor.objects.create(
                empresa=request.empresa,
                tipo=request.POST.get('tipo', 'PJ'),
                nome=request.POST.get('nome'),
                cpf_cnpj=request.POST.get('cpf_cnpj', ''),
                telefone1=request.POST.get('telefone1', ''),
                telefone2=request.POST.get('telefone2', ''),
                email=request.POST.get('email', ''),
                site=request.POST.get('site', ''),
                cep=request.POST.get('cep', ''),
                endereco=request.POST.get('endereco', ''),
                numero=request.POST.get('numero', ''),
                complemento=request.POST.get('complemento', ''),
                bairro=request.POST.get('bairro', ''),
                cidade=request.POST.get('cidade', ''),
                estado=request.POST.get('estado', ''),
                observacoes=request.POST.get('observacoes', ''),
                ativo=(request.POST.get('ativo') == 'on')
            )
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('fornecedores:lista')
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar: {e}')
            
    return render(request, 'fornecedores/form.html', {'titulo': 'Novo Fornecedor'})

@login_required
def editar(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk, empresa=request.empresa)
    
    if request.method == 'POST':
        try:
            fornecedor.tipo = request.POST.get('tipo', 'PJ')
            fornecedor.nome = request.POST.get('nome')
            fornecedor.cpf_cnpj = request.POST.get('cpf_cnpj', '')
            fornecedor.telefone1 = request.POST.get('telefone1', '')
            fornecedor.telefone2 = request.POST.get('telefone2', '')
            fornecedor.email = request.POST.get('email', '')
            fornecedor.site = request.POST.get('site', '')
            fornecedor.cep = request.POST.get('cep', '')
            fornecedor.endereco = request.POST.get('endereco', '')
            fornecedor.numero = request.POST.get('numero', '')
            fornecedor.complemento = request.POST.get('complemento', '')
            fornecedor.bairro = request.POST.get('bairro', '')
            fornecedor.cidade = request.POST.get('cidade', '')
            fornecedor.estado = request.POST.get('estado', '')
            fornecedor.observacoes = request.POST.get('observacoes', '')
            fornecedor.ativo = (request.POST.get('ativo') == 'on')
            fornecedor.save()
            
            messages.success(request, 'Fornecedor atualizado com sucesso!')
            return redirect('fornecedores:lista')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {e}')
            
    return render(request, 'fornecedores/form.html', {
        'titulo': 'Editar Fornecedor',
        'fornecedor': fornecedor
    })

@login_required
def excluir(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk, empresa=request.empresa)
    fornecedor.delete()
    messages.success(request, 'Fornecedor excluído com sucesso!')
    return redirect('fornecedores:lista')
