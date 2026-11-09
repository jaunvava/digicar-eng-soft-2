from django.contrib import admin
from .models import ContaReceber, ContaPagar, BaixaContaReceber, BaixaContaPagar


@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'descricao', 'valor', 'vencimento', 'status', 'empresa']
    list_filter = ['empresa', 'status']
    search_fields = ['cliente__nome', 'descricao']


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = ['fornecedor', 'descricao', 'valor', 'vencimento', 'status', 'empresa']
    list_filter = ['empresa', 'status']
    search_fields = ['fornecedor', 'descricao']


@admin.register(BaixaContaReceber)
class BaixaContaReceberAdmin(admin.ModelAdmin):
    list_display = ['conta', 'valor', 'data_pagamento', 'forma_pagamento']
    search_fields = ['conta__cliente__nome']


@admin.register(BaixaContaPagar)
class BaixaContaPagarAdmin(admin.ModelAdmin):
    list_display = ['conta', 'valor', 'data_pagamento', 'forma_pagamento']
    search_fields = ['conta__fornecedor']
