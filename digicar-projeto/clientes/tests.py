from django.test import TestCase
from core.models import Empresa
from .models import Cliente, Veiculo


class VeiculoTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='TST', nome='Oficina Teste')
        self.cliente = Cliente.objects.create(empresa=self.empresa, nome='Cliente Teste')

    def test_veiculo_fica_vinculado_ao_cliente_e_empresa(self):
        veiculo = Veiculo.objects.create(cliente=self.cliente, placa='ABC1D23', modelo='Civic')
        self.assertEqual(veiculo.empresa, self.empresa)
        self.assertEqual(self.cliente.veiculos.count(), 1)
