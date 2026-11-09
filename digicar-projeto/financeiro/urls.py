from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    path('receber/',                          views.contas_receber,          name='contas_receber'),
    path('receber/novo/',                     views.nova_conta_receber,      name='nova_conta_receber'),
    path('receber/<int:pk>/editar/',          views.editar_conta_receber,    name='editar_conta_receber'),
    path('receber/<int:pk>/excluir/',         views.excluir_conta_receber,   name='excluir_conta_receber'),
    path('receber/<int:pk>/imprimir/',        views.imprimir_conta,          name='imprimir_conta'),
    path('receber/<int:pk>/baixar/',          views.baixar_conta,            name='baixar_conta'),
    path('receber/exportar/',                 views.exportar_contas_receber, name='exportar_contas_receber'),
    path('pagar/',                            views.contas_pagar,            name='contas_pagar'),
    path('pagar/novo/',                       views.nova_conta_pagar,        name='nova_conta_pagar'),
    path('pagar/<int:pk>/baixar/',            views.baixar_conta_pagar,      name='baixar_conta_pagar'),
    path('baixas-receber/',                   views.baixas,                  name='baixas'),
    path('baixas-pagar/',                     views.baixas_pagar,            name='baixas_pagar'),
    path('baixas/<int:pk>/imprimir/',         views.imprimir_baixa,          name='imprimir_baixa'),
]
