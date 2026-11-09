from django.contrib import admin
from .models import Fornecedor

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf_cnpj', 'email', 'telefone1', 'ativo', 'empresa')
    list_filter = ('tipo', 'ativo', 'empresa')
    search_fields = ('nome', 'cpf_cnpj', 'email')
