from django.contrib import admin
from .models import OrdemServico, ItemOrdemServico


class ItemOSInline(admin.TabularInline):
    model = ItemOrdemServico
    extra = 0


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'equipamento', 'status', 'prioridade', 'total', 'empresa']
    list_filter = ['empresa', 'status', 'prioridade']
    search_fields = ['numero', 'cliente__nome', 'equipamento']
    inlines = [ItemOSInline]
