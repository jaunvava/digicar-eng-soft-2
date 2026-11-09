from django.db import models
from core.models import Empresa


class Cliente(models.Model):
    TIPO_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='clientes')
    tipo = models.CharField('Tipo', max_length=2, choices=TIPO_CHOICES, default='PF')
    nome = models.CharField('Nome / Razão Social', max_length=200)
    cpf_cnpj = models.CharField('CPF / CNPJ', max_length=20, blank=True)
    rg_ie = models.CharField('RG / IE', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    celular = models.CharField('Celular', max_length=20, blank=True)
    cep = models.CharField('CEP', max_length=10, blank=True)
    endereco = models.CharField('Endereço', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=10, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Veiculo(models.Model):
    """Veículo pertencente a um cliente da empresa."""

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='veiculos')
    placa = models.CharField('Placa', max_length=10)
    marca = models.CharField('Marca', max_length=100, blank=True)
    modelo = models.CharField('Modelo', max_length=100)
    ano = models.PositiveIntegerField('Ano', null=True, blank=True)
    cor = models.CharField('Cor', max_length=50, blank=True)
    chassi = models.CharField('Chassi', max_length=30, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['placa']
        constraints = [
            models.UniqueConstraint(fields=['cliente', 'placa'], name='veiculo_placa_por_cliente')
        ]

    @property
    def empresa(self):
        return self.cliente.empresa

    def __str__(self):
        return f'{self.placa} - {self.marca} {self.modelo}'.strip()
