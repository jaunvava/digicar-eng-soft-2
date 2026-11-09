from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Empresa, PerfilUsuario, BannerDashboard, ConfiguracaoEmpresa
from clientes.models import Veiculo
from produtos.models import MovimentoEstoque

admin.site.register(Veiculo)
admin.site.register(MovimentoEstoque)


class EmpresaAdminForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'


class ConfiguracaoEmpresaInline(admin.StackedInline):
    model = ConfiguracaoEmpresa
    can_delete = False
    verbose_name_plural = 'Configuração da Empresa'


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    form = EmpresaAdminForm
    list_display = ['codigo', 'nome', 'cnpj', 'ativo']
    search_fields = ['codigo', 'nome', 'cnpj']
    list_filter = ['ativo']
    inlines = [ConfiguracaoEmpresaInline]


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'empresa', 'perfil', 'ativo']
    search_fields = ['user__username', 'empresa__nome']
    list_filter = ['empresa', 'perfil', 'ativo']


@admin.register(BannerDashboard)
class BannerDashboardAdmin(admin.ModelAdmin):
    list_display = ['id', 'ordem', 'ativo', 'criado_em']
    list_editable = ['ordem', 'ativo']
    list_filter = ['ativo']
    search_fields = ['id']
