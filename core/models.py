from django.db import models
from django.contrib.auth.models import User


class Empresa(models.Model):
    codigo = models.CharField("Código", max_length=20, unique=True)
    nome = models.CharField("Nome da Empresa", max_length=200)
    cnpj = models.CharField("CNPJ", max_length=20, blank=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True)
    email = models.EmailField("E-mail", blank=True)
    endereco = models.CharField("Endereço", max_length=300, blank=True)
    logo = models.ImageField("Logo", upload_to="logos/", blank=True, null=True)
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class PerfilUsuario(models.Model):
    PERFIL_CHOICES = [
        ("admin", "Administrador"),
        ("gerente", "Gerente"),
        ("operador", "Operador"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="usuarios"
    )
    perfil = models.CharField(
        "Perfil", max_length=20, choices=PERFIL_CHOICES, default="operador"
    )
    ativo = models.BooleanField("Ativo", default=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return f"{self.user.username} - {self.empresa.nome}"


class BannerDashboard(models.Model):
    imagem = models.ImageField(
        "Imagem",
        upload_to="banners/",
        help_text="Tamanho recomendado para a imagem: 1200x320 pixels (ou proporção equivalente).",
    )
    link = models.URLField("Link de Redirecionamento", blank=True, null=True)
    ativo = models.BooleanField("Ativo", default=True)
    ordem = models.PositiveIntegerField("Ordem de Exibição", default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Banner da Dashboard"
        verbose_name_plural = "Banners da Dashboard"
        ordering = ["ordem", "-criado_em"]

    def __str__(self):
        return f"Banner {self.id}"


class ConfiguracaoEmpresa(models.Model):
    empresa = models.OneToOneField(
        Empresa, on_delete=models.CASCADE, related_name="configuracoes"
    )
    whatsapp_notificacao = models.BooleanField(
        "Enviar Cupom via WhatsApp", default=False
    )
    impressao_automatica_pdv = models.BooleanField(
        "Impressão Automática PDV", default=False
    )

    class Meta:
        verbose_name = "Configuração de Empresa"
        verbose_name_plural = "Configurações de Empresas"

    def __str__(self):
        return f"Configurações - {self.empresa.nome}"
