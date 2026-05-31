from django.db import models
from django.core.validators import RegexValidator
from core.models import Empresa


class Produto(models.Model):
    TIPO_CHOICES = [
        ('produto', 'Produto'),
        ('servico', 'Serviço'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='produtos')
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES, default='produto')
    codigo = models.CharField(
        'Código de Barras', 
        max_length=13, 
        blank=True,
        validators=[
            RegexValidator(
                r'^\d{0,13}$', 
                'O código de barras deve conter apenas números e no máximo 13 dígitos.'
            )
        ]
    )
    nome = models.CharField('Nome', max_length=200)
    unidade = models.CharField('Unidade', max_length=10, default='UN')
    preco_custo = models.DecimalField('Preço de Custo', max_digits=12, decimal_places=2, default=0)
    preco_venda = models.DecimalField('Preço de Venda', max_digits=12, decimal_places=2, default=0)
    estoque_atual = models.DecimalField('Estoque Atual', max_digits=12, decimal_places=3, default=0)
    estoque_minimo = models.DecimalField('Estoque Mínimo', max_digits=12, decimal_places=3, default=0)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return f'{self.codigo} - {self.nome}' if self.codigo else self.nome

    @property
    def margem_lucro(self):
        if self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return 0

    @property
    def estoque_baixo(self):
        return self.estoque_atual <= self.estoque_minimo
