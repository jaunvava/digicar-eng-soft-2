from django.db import models
from core.models import Empresa
from clientes.models import Cliente
from produtos.models import Produto
from django.contrib.auth.models import User


class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('em_andamento', 'Em Andamento'),
        ('aguardando_peca', 'Aguardando Peça'),
        ('pronta', 'Pronta'),
        ('entregue', 'Entregue'),
        ('cancelada', 'Cancelada'),
    ]

    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ordens_servico')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ordens_servico')
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordens_tecnico')
    numero = models.PositiveIntegerField('Número', blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='aberta')
    prioridade = models.CharField('Prioridade', max_length=10, choices=PRIORIDADE_CHOICES, default='normal')

    # Equipamento
    equipamento = models.CharField('Equipamento', max_length=200)
    marca = models.CharField('Marca', max_length=100, blank=True)
    modelo = models.CharField('Modelo', max_length=100, blank=True)
    numero_serie = models.CharField('Número de Série', max_length=100, blank=True)

    # Problema
    defeito_reclamado = models.TextField('Defeito Reclamado')
    defeito_constatado = models.TextField('Defeito Constatado', blank=True)
    solucao = models.TextField('Solução Aplicada', blank=True)

    # Datas
    data_entrada = models.DateTimeField('Data de Entrada', auto_now_add=True)
    data_prevista = models.DateField('Data Prevista', null=True, blank=True)
    data_conclusao = models.DateTimeField('Data de Conclusão', null=True, blank=True)

    # Valores
    valor_servicos = models.DecimalField('Valor dos Serviços', max_digits=12, decimal_places=2, default=0)
    valor_pecas = models.DecimalField('Valor das Peças', max_digits=12, decimal_places=2, default=0)
    desconto = models.DecimalField('Desconto', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)

    observacoes = models.TextField('Observações', blank=True)
    garantia_dias = models.PositiveIntegerField('Garantia (dias)', default=30)

    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-data_entrada']

    def __str__(self):
        return f'OS #{self.numero or self.pk} - {self.cliente.nome}'

    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = OrdemServico.objects.filter(empresa=self.empresa).order_by('-numero').first()
            self.numero = (ultimo.numero or 0) + 1 if ultimo else 1
        self.total = self.valor_servicos + self.valor_pecas - self.desconto
        super().save(*args, **kwargs)


class ItemOrdemServico(models.Model):
    TIPO_CHOICES = [
        ('servico', 'Serviço'),
        ('peca', 'Peça'),
    ]

    ordem = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name='itens')
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES, default='servico')
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True)
    descricao = models.CharField('Descrição', max_length=300)
    quantidade = models.DecimalField('Quantidade', max_digits=12, decimal_places=3, default=1)
    preco_unitario = models.DecimalField('Preço Unitário', max_digits=12, decimal_places=2)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Item de OS'
        verbose_name_plural = 'Itens de OS'

    def __str__(self):
        return f'{self.descricao} x {self.quantidade}'

    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
