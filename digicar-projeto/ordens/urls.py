from django.urls import path
from . import views

app_name = 'ordens'

urlpatterns = [
    path('',                  views.lista,         name='lista'),
    path('nova/',             views.nova,           name='nova'),
    path('<int:pk>/',         views.detalhe,        name='detalhe'),
    path('<int:pk>/status/',  views.editar_status,  name='status'),
    path('<int:pk>/excluir/', views.excluir,        name='excluir'),
    path('<int:pk>/imprimir/', views.imprimir,      name='imprimir'),
]
