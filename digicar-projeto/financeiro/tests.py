import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from clientes.models import Cliente
from core.formatacao import converter_valor, formatar_moeda
from core.models import Empresa, PerfilUsuario

from .facade import FinanceiroFacade
from .models import BaixaContaPagar, BaixaContaReceber, ContaPagar, ContaReceber
from .pagamentos import (
    ESTRATEGIAS,
    EstrategiaPagamento,
    PagamentoCartaoCredito,
    PagamentoCheque,
    PagamentoDinheiro,
    ProcessadorPagamento,
    obter_estrategia,
)


class FormatacaoTests(SimpleTestCase):
    def test_converter_valor_aceita_ponto_e_virgula(self):
        self.assertEqual(converter_valor('1234.56'), Decimal('1234.56'))
        self.assertEqual(converter_valor('1.234,56'), Decimal('1234.56'))
        self.assertEqual(converter_valor('R$ 10,5'), Decimal('10.5'))

    def test_converter_valor_invalido(self):
        with self.assertRaises(ValueError):
            converter_valor('abc')
        with self.assertRaises(ValueError):
            converter_valor('')

    def test_formatar_moeda(self):
        self.assertEqual(formatar_moeda(Decimal('1234.5')), 'R$ 1.234,50')


class EstrategiaPagamentoTests(SimpleTestCase):
    def test_estrategias_cobrem_as_formas_do_model(self):
        self.assertEqual(set(ESTRATEGIAS), set(dict(BaixaContaReceber.FORMA_CHOICES)))
        self.assertEqual(set(ESTRATEGIAS), set(dict(BaixaContaPagar.FORMA_CHOICES)))

    def test_forma_desconhecida(self):
        with self.assertRaisesMessage(ValueError, 'Forma de pagamento inválida'):
            obter_estrategia('bitcoin')

    def test_dinheiro_calcula_troco(self):
        detalhe = PagamentoDinheiro().descrever(Decimal('80'), {'valor_recebido': '100.00'})
        self.assertEqual(detalhe, 'Recebido R$ 100,00, troco R$ 20,00')

    def test_dinheiro_sem_valor_recebido_nao_descreve(self):
        self.assertEqual(PagamentoDinheiro().descrever(Decimal('80'), {'valor_recebido': '0.00'}), '')

    def test_dinheiro_recebido_menor_que_valor(self):
        with self.assertRaisesMessage(ValueError, 'menor que o valor da baixa'):
            PagamentoDinheiro().validar(Decimal('80'), {'valor_recebido': '50'})

    def test_cartao_credito_parcelado(self):
        detalhe = PagamentoCartaoCredito().descrever(Decimal('100'), {'parcelas': '3'})
        self.assertEqual(detalhe, 'Cartão de crédito em 3x de R$ 33,33')

    def test_cartao_credito_parcelas_fora_do_limite(self):
        for parcelas in ('0', '13', 'x'):
            with self.assertRaises(ValueError):
                PagamentoCartaoCredito().validar(Decimal('100'), {'parcelas': parcelas})

    def test_cheque_exige_numero(self):
        with self.assertRaisesMessage(ValueError, 'número do cheque'):
            PagamentoCheque().validar(Decimal('10'), {'numero_cheque': ' '})
        self.assertEqual(PagamentoCheque().descrever(Decimal('10'), {'numero_cheque': '42'}), 'Cheque nº 42')

    def test_processador_sem_estrategia(self):
        with self.assertRaisesMessage(ValueError, 'Selecione a forma de pagamento'):
            ProcessadorPagamento().processar(Decimal('10'), {})

    def test_processador_delega_para_a_estrategia(self):
        class EstrategiaFalsa(EstrategiaPagamento):
            chamadas = []

            def validar(self, valor, dados):
                self.chamadas.append('validar')

            def descrever(self, valor, dados):
                self.chamadas.append('descrever')
                return 'ok'

        processador = ProcessadorPagamento()
        processador.set_estrategia(EstrategiaFalsa())
        self.assertEqual(processador.processar(Decimal('1'), {}), 'ok')
        self.assertEqual(EstrategiaFalsa.chamadas, ['validar', 'descrever'])


class FinanceiroBase(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='FIN', nome='Financeiro')
        self.cliente = Cliente.objects.create(empresa=self.empresa, nome='Cliente')
        self.conta = ContaReceber.objects.create(
            empresa=self.empresa, cliente=self.cliente, descricao='Serviço',
            valor=Decimal('100.00'), vencimento=datetime.date(2030, 1, 10),
        )

    def dados(self, **extra):
        dados = {'valor': '40.00', 'data_pagamento': '2026-11-09', 'forma_pagamento': 'pix'}
        dados.update(extra)
        return dados


class FinanceiroFacadeTests(FinanceiroBase):
    def test_baixa_parcial(self):
        baixa = FinanceiroFacade().registrar_baixa_receber(self.conta, self.dados())

        self.conta.refresh_from_db()
        self.assertEqual(baixa.valor, Decimal('40.00'))
        self.assertEqual(self.conta.valor_pago, Decimal('40.00'))
        self.assertEqual(self.conta.status, 'parcial')
        self.assertIsNone(self.conta.pagamento)

    def test_baixa_total_quita_a_conta(self):
        FinanceiroFacade().registrar_baixa_receber(self.conta, self.dados(valor='100.00'))

        self.conta.refresh_from_db()
        self.assertEqual(self.conta.status, 'pago')
        self.assertEqual(self.conta.pagamento, datetime.date(2026, 11, 9))

    def test_conta_com_desconto_e_quitada_pelo_saldo(self):
        self.conta.desconto = Decimal('10.00')
        self.conta.save()

        FinanceiroFacade().registrar_baixa_receber(self.conta, self.dados(valor='90.00'))

        self.conta.refresh_from_db()
        self.assertEqual(self.conta.status, 'pago')

    def test_valor_maior_que_saldo_nao_grava(self):
        with self.assertRaisesMessage(ValueError, 'não pode ser maior que o saldo devedor'):
            FinanceiroFacade().registrar_baixa_receber(self.conta, self.dados(valor='150.00'))
        self.assertFalse(BaixaContaReceber.objects.exists())

    def test_valor_zero_e_rejeitado(self):
        with self.assertRaisesMessage(ValueError, 'maior que zero'):
            FinanceiroFacade().registrar_baixa_receber(self.conta, self.dados(valor='0'))

    def test_data_obrigatoria(self):
        with self.assertRaisesMessage(ValueError, 'data do pagamento'):
            FinanceiroFacade().registrar_baixa_receber(self.conta, self.dados(data_pagamento=''))

    def test_detalhe_da_estrategia_vai_para_observacoes(self):
        baixa = FinanceiroFacade().registrar_baixa_receber(
            self.conta,
            self.dados(forma_pagamento='cartao_credito', parcelas='2', observacoes='Balcão'),
        )
        self.assertEqual(baixa.forma_pagamento, 'cartao_credito')
        self.assertEqual(baixa.observacoes, 'Balcão\nCartão de crédito em 2x de R$ 20,00')

    def test_regra_da_estrategia_impede_a_baixa(self):
        with self.assertRaises(ValueError):
            FinanceiroFacade().registrar_baixa_receber(self.conta, self.dados(forma_pagamento='cheque'))
        self.assertFalse(BaixaContaReceber.objects.exists())

    def test_baixa_de_conta_a_pagar(self):
        conta = ContaPagar.objects.create(
            empresa=self.empresa, fornecedor='Fornecedor', descricao='Peças',
            valor=Decimal('50.00'), vencimento=datetime.date(2030, 1, 10),
        )
        baixa = FinanceiroFacade().registrar_baixa_pagar(conta, self.dados(valor='50.00'))

        conta.refresh_from_db()
        self.assertIsInstance(baixa, BaixaContaPagar)
        self.assertEqual(conta.status, 'pago')


class BaixaViewTests(FinanceiroBase):
    def setUp(self):
        super().setUp()
        usuario = User.objects.create_user('gerente', password='senha')
        PerfilUsuario.objects.create(user=usuario, empresa=self.empresa, perfil='gerente')
        self.client.login(username='gerente', password='senha')
        self.url = reverse('financeiro:baixar_conta', args=[self.conta.pk])

    def test_tela_lista_as_estrategias(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'value="cartao_credito"')
        self.assertContains(response, 'name="numero_cheque"')

    def test_post_registra_baixa(self):
        response = self.client.post(self.url, self.dados())
        self.assertRedirects(response, reverse('financeiro:contas_receber'), fetch_redirect_response=False)
        self.assertEqual(BaixaContaReceber.objects.count(), 1)

    def test_post_invalido_mostra_erro(self):
        response = self.client.post(self.url, self.dados(valor='500.00'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'não pode ser maior que o saldo devedor')
        self.assertFalse(BaixaContaReceber.objects.exists())

    def test_exportar_contas_receber_csv(self):
        response = self.client.get(reverse('financeiro:exportar_contas_receber'))
        conteudo = response.content.decode('utf-8')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="contas_receber.csv"')
        self.assertTrue(conteudo.startswith('﻿ID;Cliente;'))
        self.assertIn('Cliente;;1/1;', conteudo)
