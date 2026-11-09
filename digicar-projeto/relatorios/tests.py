import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from clientes.models import Cliente, Veiculo
from core.models import Empresa, PerfilUsuario
from produtos.models import Produto

from .exportadores import ExportadorCSV, ExportadorJSON, ExportadorRelatorio, obter_exportador
from .operacionais import (
    CRIADORES,
    DadosRelatorio,
    RelatorioClientes,
    RelatorioCreator,
    RelatorioEstoque,
    obter_criador,
)


DADOS = DadosRelatorio('Teste', ['Nome', 'Cidade'], [['Ana', 'Recife'], ['Bia; "B"', 'Natal']])


class ExportadorTemplateMethodTests(SimpleTestCase):
    def test_ordem_das_etapas(self):
        class ExportadorTexto(ExportadorRelatorio):
            content_type = 'text/plain'
            extensao = 'txt'

            def cabecalho(self, dados):
                return '[inicio]'

            def linha(self, colunas, valores):
                return '|'.join(valores)

            def separador_entre_linhas(self):
                return '/'

            def rodape(self, dados):
                return '[fim]'

        response = ExportadorTexto().exportar(DADOS, 'saida')
        self.assertEqual(response.content.decode(), '[inicio]Ana|Recife/Bia; "B"|Natal[fim]')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="saida.txt"')

    def test_linha_com_colunas_a_mais_e_rejeitada(self):
        dados = DadosRelatorio('X', ['A'], [['1', '2']])
        with self.assertRaises(ValueError):
            ExportadorCSV().exportar(dados, 'x')

    def test_csv(self):
        conteudo = ExportadorCSV().exportar(DADOS, 'r').content.decode('utf-8')
        self.assertEqual(conteudo, '﻿Nome;Cidade\r\nAna;Recife\r\n"Bia; ""B""";Natal\r\n')

    def test_json(self):
        documento = json.loads(ExportadorJSON().exportar(DADOS, 'r').content)
        self.assertEqual(documento['titulo'], 'Teste')
        self.assertEqual(documento['total'], 2)
        self.assertEqual(documento['registros'][1], {'Nome': 'Bia; "B"', 'Cidade': 'Natal'})

    def test_json_vazio_e_valido(self):
        documento = json.loads(ExportadorJSON().exportar(DadosRelatorio('V', ['A'], []), 'r').content)
        self.assertEqual(documento['registros'], [])

    def test_formato_desconhecido(self):
        self.assertIsNone(obter_exportador('pdf'))


class FactoryMethodTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='REL', nome='Relatórios')
        outra = Empresa.objects.create(codigo='OUT', nome='Outra')
        self.cliente = Cliente.objects.create(empresa=self.empresa, nome='Ana', cidade='Recife')
        Cliente.objects.create(empresa=outra, nome='Intrusa')

    def test_cada_criador_produz_seu_relatorio(self):
        self.assertIsInstance(obter_criador('clientes').criar_relatorio(), RelatorioClientes)
        self.assertIsInstance(obter_criador('estoque').criar_relatorio(), RelatorioEstoque)
        for criador in CRIADORES.values():
            self.assertTrue(issubclass(criador, RelatorioCreator))

    def test_tipo_desconhecido(self):
        self.assertIsNone(obter_criador('inexistente'))

    def test_montar_filtra_pela_empresa(self):
        dados = obter_criador('clientes').montar(self.empresa)
        self.assertEqual(dados.colunas, RelatorioClientes.colunas)
        self.assertEqual(dados.linhas, [['Ana', '—', '—', 'Recife', 'Ativo']])

    def test_estoque_formata_quantidades(self):
        Produto.objects.create(
            empresa=self.empresa, nome='Filtro', tipo='produto', unidade='UN',
            estoque_atual=Decimal('2.500'), estoque_minimo=Decimal('5'),
        )
        linha = obter_criador('estoque').montar(self.empresa).linhas[0]
        self.assertEqual(linha[2:], ['2,5 UN', '5', 'Baixo'])


class RelatorioOperacionalViewTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='VIEW', nome='Views')
        usuario = User.objects.create_user('admin', password='senha')
        PerfilUsuario.objects.create(user=usuario, empresa=self.empresa, perfil='admin')
        cliente = Cliente.objects.create(empresa=self.empresa, nome='Ana')
        Veiculo.objects.create(cliente=cliente, placa='ABC1D23', marca='Fiat', modelo='Uno')
        self.client.login(username='admin', password='senha')

    def test_tela_do_relatorio(self):
        response = self.client.get(reverse('relatorios:operacional', args=['veiculos']))
        self.assertContains(response, 'ABC1D23')
        self.assertContains(response, 'Fiat Uno')
        self.assertContains(response, reverse('relatorios:exportar_operacional', args=['veiculos', 'json']))

    def test_tipo_invalido_volta_ao_indice(self):
        response = self.client.get(reverse('relatorios:operacional', args=['xyz']))
        self.assertRedirects(response, reverse('relatorios:index'), fetch_redirect_response=False)

    def test_exportar_json(self):
        response = self.client.get(reverse('relatorios:exportar_operacional', args=['veiculos', 'json']))
        self.assertEqual(json.loads(response.content)['registros'][0]['Placa'], 'ABC1D23')

    def test_exportar_formato_invalido(self):
        response = self.client.get(reverse('relatorios:exportar_operacional', args=['veiculos', 'pdf']))
        self.assertEqual(response.status_code, 404)


class RelatorioOperacionalTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='REL', nome='Relatórios')
        user = User.objects.create_user(username='gerente', password='senha')
        PerfilUsuario.objects.create(user=user, empresa=self.empresa, perfil='gerente')
        self.client.login(username='gerente', password='senha')

    def test_relatorio_de_veiculos_existe(self):
        response = self.client.get(reverse('relatorios:operacional', args=['veiculos']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatório de Veículos')
