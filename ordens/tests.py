from django.test import TestCase
from core.models import Empresa
from clientes.models import Cliente, Veiculo
from .models import OrdemServico
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import PerfilUsuario
from produtos.models import Produto, MovimentoEstoque


class OrdemVeiculoTests(TestCase):
    def test_ordem_pode_ser_consultada_por_veiculo(self):
        empresa = Empresa.objects.create(codigo='OS', nome='Oficina')
        cliente = Cliente.objects.create(empresa=empresa, nome='Cliente')
        veiculo = Veiculo.objects.create(cliente=cliente, placa='XYZ9A99', modelo='Gol')
        os = OrdemServico.objects.create(empresa=empresa, cliente=cliente, veiculo=veiculo,
            equipamento='Veículo', defeito_reclamado='Revisão')
        self.assertEqual(veiculo.ordens_servico.get(), os)

    def test_peca_na_ordem_baixa_estoque_e_registra_movimento(self):
        empresa = Empresa.objects.create(codigo='OS2', nome='Oficina 2')
        cliente = Cliente.objects.create(empresa=empresa, nome='Cliente')
        veiculo = Veiculo.objects.create(cliente=cliente, placa='QWE1A23', modelo='Uno')
        produto = Produto.objects.create(empresa=empresa, nome='Filtro', tipo='produto', estoque_atual=10, preco_venda=20)
        user = User.objects.create_user('admin-os', password='senha')
        PerfilUsuario.objects.create(user=user, empresa=empresa, perfil='admin')
        self.client.login(username='admin-os', password='senha')
        response = self.client.post(reverse('ordens:nova'), {
            'cliente': cliente.pk, 'veiculo': veiculo.pk, 'status': 'aberta', 'prioridade': 'normal',
            'equipamento': 'Automóvel', 'defeito_reclamado': 'Revisão', 'garantia_dias': 30, 'desconto': 0,
            'item_tipo': ['peca'], 'item_produto': [str(produto.pk)], 'item_descricao': ['Filtro'],
            'item_quantidade': ['2'], 'item_preco': ['20'],
        })
        self.assertEqual(response.status_code, 302)
        produto.refresh_from_db()
        self.assertEqual(produto.estoque_atual, 8)
        self.assertTrue(MovimentoEstoque.objects.filter(produto=produto, tipo='saida', quantidade=2).exists())
