from django.urls import path
from . import views

app_name = 'orcamentos'

urlpatterns = [
    path('',              views.lista,          name='lista'),
    path('novo/',         views.novo,           name='novo'),
    path('<int:pk>/',     views.detalhe,        name='detalhe'),
    path('<int:pk>/status/', views.alterar_status, name='status'),
    path('<int:pk>/imprimir/', views.imprimir,     name='imprimir'),
]
