from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('',                   views.lista,          name='lista'),
    path('novo/',              views.novo,           name='novo'),
    path('imprimir/',          views.imprimir,       name='imprimir'),
    path('exportar-excel/',    views.exportar_excel, name='exportar_excel'),
    path('<int:pk>/',          views.detalhe,        name='detalhe'),
    path('<int:pk>/editar/',   views.editar,         name='editar'),
    path('<int:pk>/excluir/',  views.excluir,        name='excluir'),
]

