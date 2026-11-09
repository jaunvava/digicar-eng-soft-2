from django.db import models
from core.models import Empresa

class Fornecedor(models.Model):
    TIPO_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='fornecedores')
    tipo = models.CharField('Tipo de Pessoa', max_length=2, choices=TIPO_CHOICES, default='PJ')
    nome = models.CharField('Nome / Razão Social', max_length=200)
    cpf_cnpj = models.CharField('CPF / CNPJ', max_length=20, blank=True)
    
    # Contato
    telefone1 = models.CharField('Telefone 1', max_length=20, blank=True)
    telefone2 = models.CharField('Telefone 2', max_length=20, blank=True)
    email = models.EmailField('E-mail', max_length=100, blank=True)
    site = models.URLField('Site', max_length=200, blank=True)
    
    # Endereço
    cep = models.CharField('CEP', max_length=10, blank=True)
    endereco = models.CharField('Endereço', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=20, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)
    
    # Adicionais
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['nome']

    def __str__(self):
        return self.nome
