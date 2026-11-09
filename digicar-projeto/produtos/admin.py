from django.contrib import admin
from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'tipo', 'preco_venda', 'estoque_atual', 'empresa', 'ativo']
    search_fields = ['nome', 'codigo']
    list_filter = ['empresa', 'tipo', 'ativo']
