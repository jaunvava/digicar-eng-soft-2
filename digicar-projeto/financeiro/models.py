import datetime
from django.db import models
from core.models import Empresa
from clientes.models import Cliente


class ContaReceber(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('parcial', 'Parcial'),
        ('pago', 'Pago'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='contas_receber')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contas_receber')
    numero_titulo = models.CharField('Nº Título', max_length=50, blank=True)
    descricao = models.CharField('Descrição', max_length=300)
    parcela = models.CharField('Parcela', max_length=10, default='1/1')
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    valor_pago = models.DecimalField('Valor Pago', max_digits=12, decimal_places=2, default=0)
    desconto = models.DecimalField('Desconto', max_digits=12, decimal_places=2, default=0)
    emissao = models.DateField('Data Emissão', default=datetime.date.today)
    vencimento = models.DateField('Vencimento')
    pagamento = models.DateField('Data de Pagamento', null=True, blank=True)
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='pendente')
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
        ordering = ['vencimento']

    def __str__(self):
        return f'{self.cliente.nome} - R$ {self.valor} - {self.vencimento}'

    @property
    def saldo_devedor(self):
        return self.valor - self.valor_pago - self.desconto


class ContaPagar(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('parcial', 'Parcial'),
        ('pago', 'Pago'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='contas_pagar')
    fornecedor = models.CharField('Fornecedor', max_length=200)
    numero_titulo = models.CharField('Nº Título', max_length=50, blank=True)
    descricao = models.CharField('Descrição', max_length=300)
    parcela = models.CharField('Parcela', max_length=10, default='1/1')
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    valor_pago = models.DecimalField('Valor Pago', max_digits=12, decimal_places=2, default=0)
    desconto = models.DecimalField('Desconto', max_digits=12, decimal_places=2, default=0)
    emissao = models.DateField('Data Emissão', auto_now_add=True)
    vencimento = models.DateField('Vencimento')
    pagamento = models.DateField('Data de Pagamento', null=True, blank=True)
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='pendente')
    categoria = models.CharField('Categoria', max_length=100, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
        ordering = ['vencimento']

    def __str__(self):
        return f'{self.fornecedor} - R$ {self.valor} - {self.vencimento}'

    @property
    def saldo_devedor(self):
        return self.valor - self.valor_pago - self.desconto


class BaixaContaReceber(models.Model):
    FORMA_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_debito', 'Cartão de Débito'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('transferencia', 'Transferência'),
        ('boleto', 'Boleto'),
        ('cheque', 'Cheque'),
    ]

    conta = models.ForeignKey(ContaReceber, on_delete=models.CASCADE, related_name='baixas')
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    data_pagamento = models.DateField('Data de Pagamento')
    forma_pagamento = models.CharField('Forma de Pagamento', max_length=20, choices=FORMA_CHOICES)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Baixa de Conta a Receber'
        verbose_name_plural = 'Baixas de Contas a Receber'

    def __str__(self):
        return f'Baixa {self.conta} - R$ {self.valor}'


class BaixaContaPagar(models.Model):
    FORMA_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_debito', 'Cartão de Débito'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('transferencia', 'Transferência'),
        ('boleto', 'Boleto'),
        ('cheque', 'Cheque'),
    ]

    conta = models.ForeignKey(ContaPagar, on_delete=models.CASCADE, related_name='baixas')
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    data_pagamento = models.DateField('Data de Pagamento')
    forma_pagamento = models.CharField('Forma de Pagamento', max_length=20, choices=FORMA_CHOICES)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Baixa de Conta a Pagar'
        verbose_name_plural = 'Baixas de Contas a Pagar'

    def __str__(self):
        return f'Baixa {self.conta} - R$ {self.valor}'
