from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('',                   views.lista,           name='lista'),
    path('novo/',              views.novo,             name='novo'),
    path('imprimir/',          views.imprimir,         name='imprimir'),
    path('exportar/',          views.exportar_excel,   name='exportar_excel'),
    path('<int:pk>/editar/',   views.editar,           name='editar'),
    path('<int:pk>/excluir/',  views.excluir,          name='excluir'),
    path('<int:pk>/estoque/',  views.estoque,          name='estoque'),
]
