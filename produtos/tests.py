from decimal import Decimal
from django.test import TestCase
from core.models import Empresa
from .models import Produto, MovimentoEstoque


class EstoqueTests(TestCase):
    def setUp(self):
        empresa = Empresa.objects.create(codigo='EST', nome='Estoque Teste')
        self.produto = Produto.objects.create(empresa=empresa, nome='Pastilha', tipo='produto', estoque_atual=10)

    def test_movimentacao_registra_saldo_anterior_e_posterior(self):
        movimento = MovimentoEstoque.objects.create(produto=self.produto, tipo='entrada', quantidade=5,
            estoque_anterior=10, estoque_posterior=15, motivo='Compra')
        self.assertEqual(movimento.estoque_posterior, Decimal('15'))
