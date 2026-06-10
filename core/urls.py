from django.urls import include, path
from . import views

app_name = 'core'

urlpatterns = [
    path('dashboard/',     views.dashboard,          name='dashboard'),
    path('',               views.login_view,         name='login'),
    path('logout/',        views.logout_view,        name='logout'),
    path('perfil/',        views.perfil_view,        name='perfil'),
    path('configuracoes/', views.configuracoes_view, name='configuracoes'),
    path('notificacoes/',  views.notificacoes_json,  name='notificacoes'),
    path('aplicativos/',   views.aplicativos_view,   name='aplicativos'),
    path('accounts/', include('django.contrib.auth.urls')),
]
