from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from clientes.models import Cliente
from core.models import Empresa
from financeiro.models import BaixaContaReceber, ContaReceber
from ordens.models import OrdemServico
from produtos.models import Produto


class SeedDemoTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='1', nome='teste')

    def test_popula_com_dados_coerentes(self):
        call_command('seed_demo', stdout=StringIO())

        self.assertEqual(Cliente.objects.filter(empresa=self.empresa).count(), 32)
        self.assertTrue(OrdemServico.objects.filter(empresa=self.empresa).exists())
        self.assertTrue(BaixaContaReceber.objects.filter(conta__empresa=self.empresa).exists())
        self.assertTrue(ContaReceber.objects.filter(empresa=self.empresa, status='atrasado').exists())
        # Estoque nunca fica negativo.
        self.assertFalse(Produto.objects.filter(empresa=self.empresa, estoque_atual__lt=0).exists())
        # Toda conta paga está quitada.
        for conta in ContaReceber.objects.filter(empresa=self.empresa, status='pago'):
            self.assertEqual(conta.saldo_devedor, 0)

    def test_nao_duplica_sem_limpar(self):
        call_command('seed_demo', stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command('seed_demo', stdout=StringIO())
        call_command('seed_demo', '--limpar', stdout=StringIO())
        self.assertEqual(Cliente.objects.filter(empresa=self.empresa).count(), 32)
