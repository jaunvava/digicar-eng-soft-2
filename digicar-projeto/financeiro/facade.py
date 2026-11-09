"""Padrao Facade: ponto de entrada unico para registrar baixas.

A view chama um metodo e recebe a baixa pronta. A Facade esconde os
subsistemas envolvidos: conversao do valor, regras da forma de pagamento
(Strategy), criacao do registro de baixa, atualizacao de saldo/status da
conta e a transacao no banco.
"""
from django.db import transaction
from django.utils.dateparse import parse_date

from core.formatacao import converter_valor, formatar_moeda

from .models import BaixaContaPagar, BaixaContaReceber
from .pagamentos import ProcessadorPagamento, obter_estrategia


class FinanceiroFacade:

    def registrar_baixa_receber(self, conta, dados) -> BaixaContaReceber:
        return self._registrar_baixa(conta, BaixaContaReceber, dados)

    def registrar_baixa_pagar(self, conta, dados) -> BaixaContaPagar:
        return self._registrar_baixa(conta, BaixaContaPagar, dados)

    def _registrar_baixa(self, conta, modelo_baixa, dados):
        valor = converter_valor(dados.get('valor'))
        data_pagamento = self._data_pagamento(dados)
        estrategia = obter_estrategia(dados.get('forma_pagamento'))
        detalhe = ProcessadorPagamento(estrategia).processar(valor, dados)

        with transaction.atomic():
            # Relê a conta travada para que duas baixas simultâneas não
            # ultrapassem o saldo devedor.
            conta = type(conta).objects.select_for_update().get(pk=conta.pk)
            self._validar_valor(valor, conta)

            baixa = modelo_baixa.objects.create(
                conta=conta,
                valor=valor,
                data_pagamento=data_pagamento,
                forma_pagamento=estrategia.codigo,
                observacoes=self._observacoes(dados, detalhe),
            )
            self._atualizar_conta(conta, valor, data_pagamento)
        return baixa

    @staticmethod
    def _data_pagamento(dados):
        texto = dados.get('data_pagamento') or ''
        data = parse_date(texto)
        if data is None:
            raise ValueError('Informe a data do pagamento.')
        return data

    @staticmethod
    def _validar_valor(valor, conta):
        if valor <= 0:
            raise ValueError('O valor da baixa deve ser maior que zero.')
        if valor > conta.saldo_devedor:
            raise ValueError(
                f'O valor da baixa ({formatar_moeda(valor)}) não pode ser maior que o '
                f'saldo devedor ({formatar_moeda(conta.saldo_devedor)}).'
            )

    @staticmethod
    def _observacoes(dados, detalhe):
        partes = [str(dados.get('observacoes', '')).strip(), detalhe]
        return '\n'.join(parte for parte in partes if parte)

    @staticmethod
    def _atualizar_conta(conta, valor, data_pagamento):
        conta.valor_pago += valor
        # saldo_devedor já desconta o desconto concedido.
        if conta.saldo_devedor <= 0:
            conta.status = 'pago'
            conta.pagamento = data_pagamento
        else:
            conta.status = 'parcial'
        conta.save()
