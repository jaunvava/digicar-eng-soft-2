from django.db import models
from core.models import Empresa
from clientes.models import Cliente
from produtos.models import Produto
from django.contrib.auth.models import User


class Orcamento(models.Model):
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('enviado', 'Enviado'),
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
        ('expirado', 'Expirado'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='orcamentos')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='orcamentos')
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    numero = models.PositiveIntegerField('Número', blank=True, null=True)
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='rascunho')
    validade = models.DateField('Validade')
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=0)
    desconto = models.DecimalField('Desconto', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Orçamento #{self.numero or self.pk} - {self.cliente.nome}'

    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = Orcamento.objects.filter(empresa=self.empresa).order_by('-numero').first()
            self.numero = (ultimo.numero or 0) + 1 if ultimo else 1
        super().save(*args, **kwargs)


class ItemOrcamento(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.DecimalField('Quantidade', max_digits=12, decimal_places=3)
    preco_unitario = models.DecimalField('Preço Unitário', max_digits=12, decimal_places=2)
    desconto = models.DecimalField('Desconto', max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Item de Orçamento'
        verbose_name_plural = 'Itens de Orçamento'

    def __str__(self):
        return f'{self.produto.nome} x {self.quantidade}'

    def save(self, *args, **kwargs):
        self.subtotal = (self.quantidade * self.preco_unitario) - self.desconto
        super().save(*args, **kwargs)
