import datetime
import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente, Veiculo
from core.models import Empresa, PerfilUsuario
from financeiro.models import ContaReceber
from fornecedores.models import Fornecedor
from ordens.models import OrdemServico
from produtos.models import Produto


def json_do_script(html, script_id):
    inicio = html.index(f'id="{script_id}"')
    inicio = html.index('>', inicio) + 1
    fim = html.index('</script>', inicio)
    return json.loads(html[inicio:fim])


class InterfaceBase(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='UI', nome='Interface')
        usuario = User.objects.create_user('admin', password='senha')
        PerfilUsuario.objects.create(user=usuario, empresa=self.empresa, perfil='admin')
        self.client.login(username='admin', password='senha')
        self.cliente = Cliente.objects.create(empresa=self.empresa, nome="Joana D'Arc")


class ExclusaoSomentePostTests(InterfaceBase):
    def alvos(self):
        veiculo = Veiculo.objects.create(cliente=self.cliente, placa='ABC1D23', modelo='Uno')
        produto = Produto.objects.create(empresa=self.empresa, nome='Filtro')
        fornecedor = Fornecedor.objects.create(empresa=self.empresa, nome='Fornecedor')
        ordem = OrdemServico.objects.create(
            empresa=self.empresa, cliente=self.cliente, equipamento='Uno', defeito_reclamado='Barulho',
        )
        return [
            ('clientes:excluir_veiculo', veiculo),
            ('produtos:excluir', produto),
            ('fornecedores:excluir', fornecedor),
            ('ordens:excluir', ordem),
            ('clientes:excluir', self.cliente),
        ]

    def test_get_nao_exclui(self):
        for rota, objeto in self.alvos():
            with self.subTest(rota=rota):
                response = self.client.get(reverse(rota, args=[objeto.pk]))
                self.assertEqual(response.status_code, 405)
                self.assertTrue(type(objeto).objects.filter(pk=objeto.pk).exists())

    def test_post_exclui(self):
        for rota, objeto in self.alvos():
            with self.subTest(rota=rota):
                self.client.post(reverse(rota, args=[objeto.pk]))
                self.assertFalse(type(objeto).objects.filter(pk=objeto.pk).exists())

    def test_lista_usa_formulario_com_confirmacao(self):
        response = self.client.get(reverse('clientes:lista'))
        self.assertContains(response, 'data-confirm="Excluir Joana D&#x27;Arc?"')
        self.assertContains(response, 'data-confirm-perigo')
        self.assertNotContains(response, 'confirmDelete(')


class MensagensSweetAlertTests(InterfaceBase):
    def test_mensagens_vao_como_json(self):
        response = self.client.post(reverse('clientes:excluir', args=[self.cliente.pk]), follow=True)
        mensagens = json_do_script(response.content.decode(), 'mensagens-django')
        self.assertEqual(mensagens, [{'nivel': 'success', 'texto': 'Cliente excluído com sucesso!'}])

    def test_paginas_carregam_alertas_e_graficos_sem_dark_mode(self):
        html = self.client.get(reverse('core:dashboard')).content.decode()
        self.assertIn('js/alertas.js', html)
        self.assertIn('js/graficos.js', html)
        self.assertNotIn('dark_mode_switch', html)
        self.assertIn('data-bs-theme="light"', html)

    def test_login_mostra_erro_pelo_sweetalert(self):
        self.client.logout()
        response = self.client.post(reverse('core:login'), {'codigo_empresa': 'XX', 'username': 'a', 'password': 'b'})
        html = response.content.decode()
        self.assertIn('js/alertas.js', html)
        self.assertEqual(json_do_script(html, 'mensagens-django')[0]['nivel'], 'error')
        self.assertNotIn('alert alert-danger', html)


class GraficosTests(InterfaceBase):
    def test_dashboard_envia_dados_numericos(self):
        ContaReceber.objects.create(
            empresa=self.empresa, cliente=self.cliente, descricao='Serviço',
            valor=Decimal('1234.56'), vencimento=datetime.date(2030, 1, 1), status='pago',
        )
        OrdemServico.objects.create(
            empresa=self.empresa, cliente=self.cliente, equipamento='Uno',
            defeito_reclamado='Barulho', status='pronta',
        )
        html = self.client.get(reverse('core:dashboard')).content.decode()

        recebimentos = json_do_script(html, 'dados-recebimentos')
        self.assertEqual(recebimentos['valores'], [0.0, 1234.56, 0.0])

        ordens = json_do_script(html, 'dados-ordens')
        self.assertEqual(ordens['valores'][ordens['chaves'].index('pronta')], 1)
        self.assertEqual(sum(ordens['valores']), 1)

    def test_relatorio_financeiro_envia_devedores(self):
        ContaReceber.objects.create(
            empresa=self.empresa, cliente=self.cliente, descricao='Peças',
            valor=Decimal('300.00'), vencimento=datetime.date(2020, 1, 1), status='atrasado',
        )
        html = self.client.get(reverse('relatorios:financeiro')).content.decode()
        dados = json_do_script(html, 'dados-devedores')
        self.assertEqual(dados, {'rotulos': ["Joana D'Arc"], 'valores': [300.0]})


class RotasDeLoginTests(TestCase):
    def test_login_e_logout_usam_as_views_do_sistema(self):
        self.assertEqual(reverse('core:login'), '/')
        self.assertEqual(reverse('core:logout'), '/logout/')

    def test_logout_pelo_link_da_sidebar(self):
        empresa = Empresa.objects.create(codigo='LG', nome='Logout')
        usuario = User.objects.create_user('u', password='senha')
        PerfilUsuario.objects.create(user=usuario, empresa=empresa, perfil='admin')
        self.client.login(username='u', password='senha')
        response = self.client.get(reverse('core:logout'))
        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', self.client.session)


class RodapeERelatoriosTests(InterfaceBase):
    def test_rodape_mostra_versao_semantica_sem_suporte(self):
        from digicar import __version__
        self.assertRegex(__version__, r'^\d+\.\d+\.\d+$')
        html = self.client.get(reverse('core:dashboard')).content.decode()
        self.assertIn(f'v{__version__}', html)
        self.assertNotIn('supportModal', html)

    def test_relatorios_mostram_os_cinco_relatorios(self):
        html = self.client.get(reverse('relatorios:index')).content.decode()
        self.assertEqual(html.count('class="relatorio-linha"'), 5)
        self.assertIn('Financeiro', html)
        self.assertIn('Operacional', html)
        self.assertIn(reverse('relatorios:operacional', args=['estoque']), html)

    def test_contas_a_pagar_sem_cards_de_total(self):
        html = self.client.get(reverse('financeiro:contas_pagar')).content.decode()
        self.assertNotIn('Total Pendente', html)
        self.assertIn('card-filtros', html)
