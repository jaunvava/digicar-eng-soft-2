from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from .models import Empresa, PerfilUsuario, BannerDashboard, ConfiguracaoEmpresa


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


class BannerDashboardForm(forms.ModelForm):
    arquivo_imagem = forms.ImageField(
        label='Imagem',
        required=False,
        help_text='Envie uma nova imagem para substituir a atual. Tamanho recomendado: 1200x320 pixels.',
    )

    class Meta:
        model = BannerDashboard
        fields = ['link', 'ativo', 'ordem']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['arquivo_imagem'].required = True

    def save(self, commit=True):
        banner = super().save(commit=False)
        arquivo = self.cleaned_data.get('arquivo_imagem')
        if arquivo:
            banner.imagem = arquivo.read()
            banner.imagem_tipo = arquivo.content_type or 'image/jpeg'
            banner.imagem_nome = arquivo.name
        if commit:
            banner.save()
        return banner


@admin.register(BannerDashboard)
class BannerDashboardAdmin(admin.ModelAdmin):
    form = BannerDashboardForm
    list_display = ['id', 'preview', 'ordem', 'ativo', 'criado_em']
    list_editable = ['ordem', 'ativo']
    list_filter = ['ativo']
    search_fields = ['id']
    readonly_fields = ['preview']
    fields = ['preview', 'arquivo_imagem', 'link', 'ativo', 'ordem']

    def preview(self, obj):
        if obj.pk and obj.imagem:
            url = reverse('core:banner_imagem', args=[obj.pk])
            return format_html('<img src="{}" style="max-height:120px;border-radius:4px;" alt="Banner">', url)
        return '—'
    preview.short_description = 'Pré-visualização'
