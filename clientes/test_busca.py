from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Empresa, PerfilUsuario
from financeiro.models import ContaReceber
from orcamentos.models import Orcamento

from .models import Cliente, Veiculo


class BuscaBase(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='BC', nome='Busca')
        self.outra = Empresa.objects.create(codigo='OU', nome='Outra')
        usuario = User.objects.create_user('gerente', password='senha')
        PerfilUsuario.objects.create(user=usuario, empresa=self.empresa, perfil='gerente')
        self.client.login(username='gerente', password='senha')

    def buscar(self, **params):
        return self.client.get(reverse('clientes:buscar'), params).json()


class BuscaClientesTests(BuscaBase):
    def test_pagina_de_20_e_carrega_mais(self):
        for i in range(45):
            Cliente.objects.create(empresa=self.empresa, nome=f'Cliente {i:02d}')

        p1 = self.buscar()
        p3 = self.buscar(pagina=3)

        self.assertEqual(len(p1['resultados']), 20)
        self.assertTrue(p1['tem_mais'])
        self.assertEqual(len(p3['resultados']), 5)
        self.assertFalse(p3['tem_mais'])
        self.assertEqual(p1['resultados'][0]['nome'], 'Cliente 00')

    def test_busca_por_nome_documento_telefone_e_codigo(self):
        ana = Cliente.objects.create(empresa=self.empresa, nome='Ana Souza', cpf_cnpj='383.004.030-00',
                                     celular='(81) 98441-7390')
        Cliente.objects.create(empresa=self.empresa, nome='Bruno Lima')

        for termo in ('souza', '38300403000', '383.004', '984417390', str(ana.pk)):
            with self.subTest(termo=termo):
                nomes = [r['nome'] for r in self.buscar(q=termo)['resultados']]
                self.assertIn('Ana Souza', nomes)
                self.assertNotIn('Bruno Lima', nomes)

    def test_nao_traz_inativos_nem_de_outra_empresa(self):
        Cliente.objects.create(empresa=self.empresa, nome='Ativo')
        Cliente.objects.create(empresa=self.empresa, nome='Inativo', ativo=False)
        Cliente.objects.create(empresa=self.outra, nome='Intruso')
        self.assertEqual([r['nome'] for r in self.buscar()['resultados']], ['Ativo'])

    def test_veiculos_do_cliente_respeita_a_empresa(self):
        meu = Cliente.objects.create(empresa=self.empresa, nome='Meu')
        dele = Cliente.objects.create(empresa=self.outra, nome='Dele')
        Veiculo.objects.create(cliente=meu, placa='AAA1A11', marca='Fiat', modelo='Uno')
        Veiculo.objects.create(cliente=dele, placa='BBB2B22', modelo='Gol')

        dados = self.client.get(reverse('clientes:veiculos_json', args=[meu.pk])).json()
        self.assertEqual(dados['resultados'][0]['placa'], 'AAA1A11')
        self.assertEqual(self.client.get(reverse('clientes:veiculos_json', args=[dele.pk])).status_code, 404)


class FormulariosSemListaInteiraTests(BuscaBase):
    def test_formularios_nao_carregam_todos_os_clientes(self):
        Cliente.objects.create(empresa=self.empresa, nome='Cliente Escondido')
        for rota in ('clientes:novo_veiculo', 'financeiro:nova_conta_receber', 'orcamentos:novo', 'ordens:nova'):
            with self.subTest(rota=rota):
                html = self.client.get(reverse(rota)).content.decode()
                self.assertIn('data-busca-cliente', html)
                self.assertNotIn('Cliente Escondido', html)


class VeiculoFormTests(BuscaBase):
    def setUp(self):
        super().setUp()
        self.dono = Cliente.objects.create(empresa=self.empresa, nome='Dono')

    def dados(self, **extra):
        dados = {'cliente': self.dono.pk, 'placa': 'abc-1d23', 'modelo': 'Onix'}
        dados.update(extra)
        return dados

    def test_cadastra_normalizando_a_placa(self):
        self.client.post(reverse('clientes:novo_veiculo'), self.dados())
        self.assertEqual(Veiculo.objects.get().placa, 'ABC1D23')

    def test_exige_cliente(self):
        response = self.client.post(reverse('clientes:novo_veiculo'), self.dados(cliente=''))
        self.assertContains(response, 'Selecione um cliente da lista')
        self.assertFalse(Veiculo.objects.exists())

    def test_recusa_cliente_de_outra_empresa(self):
        intruso = Cliente.objects.create(empresa=self.outra, nome='Intruso')
        self.client.post(reverse('clientes:novo_veiculo'), self.dados(cliente=intruso.pk))
        self.assertFalse(Veiculo.objects.exists())

    def test_placa_repetida_vira_mensagem(self):
        Veiculo.objects.create(cliente=self.dono, placa='ABC1D23', modelo='Onix')
        response = self.client.post(reverse('clientes:novo_veiculo'), self.dados())
        self.assertContains(response, 'já tem um veículo com a placa ABC1D23')

    def test_ano_invalido_vira_mensagem(self):
        veiculo = Veiculo.objects.create(cliente=self.dono, placa='ABC1D23', modelo='Onix')
        response = self.client.post(reverse('clientes:editar_veiculo', args=[veiculo.pk]), self.dados(ano='abc'))
        self.assertContains(response, 'Ano inválido')

    def test_edicao_mantem_dono_inativo(self):
        veiculo = Veiculo.objects.create(cliente=self.dono, placa='ABC1D23', modelo='Onix')
        self.dono.ativo = False
        self.dono.save()

        html = self.client.get(reverse('clientes:editar_veiculo', args=[veiculo.pk])).content.decode()
        self.assertIn(f'value="{self.dono.pk}"', html)

        self.client.post(reverse('clientes:editar_veiculo', args=[veiculo.pk]), self.dados(modelo='Onix LT'))
        veiculo.refresh_from_db()
        self.assertEqual((veiculo.cliente_id, veiculo.modelo), (self.dono.pk, 'Onix LT'))

    def test_atalho_da_tela_do_cliente_preenche_o_dono(self):
        html = self.client.get(reverse('clientes:novo_veiculo'), {'cliente': self.dono.pk}).content.decode()
        self.assertIn('value="Dono"', html)


class ClienteDeOutraEmpresaTests(BuscaBase):
    def test_orcamento_e_conta_recusam_cliente_de_outra_empresa(self):
        intruso = Cliente.objects.create(empresa=self.outra, nome='Intruso')
        self.client.post(reverse('orcamentos:novo'), {'cliente': intruso.pk, 'validade': '2030-01-01'})
        self.client.post(reverse('financeiro:nova_conta_receber'),
                         {'cliente': intruso.pk, 'valor': '10.00', 'vencimento': '2030-01-01'})
        self.assertFalse(Orcamento.objects.exists())
        self.assertFalse(ContaReceber.objects.exists())
