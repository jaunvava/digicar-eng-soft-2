from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('',                   views.lista,          name='lista'),
    path('novo/',              views.novo,           name='novo'),
    path('imprimir/',          views.imprimir,       name='imprimir'),
    path('exportar-excel/',    views.exportar_excel, name='exportar_excel'),
    path('veiculos/',          views.veiculos,        name='veiculos'),
    path('veiculos/novo/',     views.novo_veiculo,    name='novo_veiculo'),
    path('veiculos/<int:pk>/editar/', views.editar_veiculo, name='editar_veiculo'),
    path('veiculos/<int:pk>/', views.detalhe_veiculo, name='detalhe_veiculo'),
    path('veiculos/<int:pk>/excluir/', views.excluir_veiculo, name='excluir_veiculo'),
    path('<int:pk>/',          views.detalhe,        name='detalhe'),
    path('<int:pk>/editar/',   views.editar,         name='editar'),
    path('<int:pk>/excluir/',  views.excluir,        name='excluir'),
]
