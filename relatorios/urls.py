from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.index, name='index'),
    path('financeiro/', views.relatorio_financeiro, name='financeiro'),
]
