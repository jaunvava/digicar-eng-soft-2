from django.contrib import admin
from .models import Orcamento, ItemOrcamento


class ItemOrcInline(admin.TabularInline):
    model = ItemOrcamento
    extra = 0


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'total', 'status', 'validade', 'empresa']
    list_filter = ['empresa', 'status']
    inlines = [ItemOrcInline]
