from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'cpf_cnpj', 'telefone', 'cidade', 'empresa', 'ativo']
    search_fields = ['nome', 'cpf_cnpj']
    list_filter = ['empresa', 'tipo', 'ativo']
