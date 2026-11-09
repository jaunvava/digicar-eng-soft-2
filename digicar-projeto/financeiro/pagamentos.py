"""Padrao Strategy: cada forma de pagamento da baixa e uma estrategia.

O ProcessadorPagamento (contexto) nao sabe qual forma esta usando; ele so
chama validar() e descrever(). Uma forma nova e uma classe nova registrada em
ESTRATEGIAS, sem mexer no processador nem nas views.
"""
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

from core.formatacao import converter_valor, formatar_moeda


class EstrategiaPagamento(ABC):
    """Interface (Strategy) comum a todas as formas de pagamento."""

    codigo = ''
    nome = ''
    icone = ''

    def validar(self, valor: Decimal, dados) -> None:
        """Gancho: por padrao a forma de pagamento nao exige dados extras."""

    @abstractmethod
    def descrever(self, valor: Decimal, dados) -> str:
        """Complemento gravado nas observacoes da baixa ('' quando nao ha)."""


class PagamentoSimples(EstrategiaPagamento):
    """Formas sem regra propria (PIX, debito, transferencia, boleto)."""

    def __init__(self, codigo, nome, icone):
        self.codigo = codigo
        self.nome = nome
        self.icone = icone

    def descrever(self, valor, dados):
        return ''


class PagamentoDinheiro(EstrategiaPagamento):
    """Calcula o troco quando o valor recebido e informado."""

    codigo = 'dinheiro'
    nome = 'Dinheiro'
    icone = '💵'

    def _valor_recebido(self, dados):
        texto = dados.get('valor_recebido', '')
        if not str(texto).strip():
            return None
        recebido = converter_valor(texto)
        # O campo com mascara envia 0.00 quando fica em branco.
        return recebido if recebido > 0 else None

    def validar(self, valor, dados):
        recebido = self._valor_recebido(dados)
        if recebido is not None and recebido < valor:
            raise ValueError(
                f'Valor recebido ({formatar_moeda(recebido)}) menor que o valor da baixa '
                f'({formatar_moeda(valor)}).'
            )

    def descrever(self, valor, dados):
        recebido = self._valor_recebido(dados)
        if recebido is None:
            return ''
        return f'Recebido {formatar_moeda(recebido)}, troco {formatar_moeda(recebido - valor)}'


class PagamentoCartaoCredito(EstrategiaPagamento):
    """Exige o numero de parcelas e registra o valor de cada uma."""

    codigo = 'cartao_credito'
    nome = 'Cartão de Crédito'
    icone = '💳'
    MAX_PARCELAS = 12

    def _parcelas(self, dados):
        try:
            parcelas = int(dados.get('parcelas') or 1)
        except (TypeError, ValueError) as exc:
            raise ValueError('Número de parcelas inválido.') from exc
        if not 1 <= parcelas <= self.MAX_PARCELAS:
            raise ValueError(f'Parcelas devem estar entre 1 e {self.MAX_PARCELAS}.')
        return parcelas

    def validar(self, valor, dados):
        self._parcelas(dados)

    def descrever(self, valor, dados):
        parcelas = self._parcelas(dados)
        valor_parcela = (valor / parcelas).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return f'Cartão de crédito em {parcelas}x de {formatar_moeda(valor_parcela)}'


class PagamentoCheque(EstrategiaPagamento):
    """Exige o numero do cheque."""

    codigo = 'cheque'
    nome = 'Cheque'
    icone = '📝'

    def _numero(self, dados):
        return str(dados.get('numero_cheque', '')).strip()

    def validar(self, valor, dados):
        if not self._numero(dados):
            raise ValueError('Informe o número do cheque.')

    def descrever(self, valor, dados):
        return f'Cheque nº {self._numero(dados)}'


class ProcessadorPagamento:
    """Contexto do Strategy: usa a estrategia sem saber qual ela e."""

    def __init__(self, estrategia: EstrategiaPagamento = None):
        self.estrategia = estrategia

    def set_estrategia(self, estrategia: EstrategiaPagamento) -> None:
        self.estrategia = estrategia

    def processar(self, valor: Decimal, dados) -> str:
        if self.estrategia is None:
            raise ValueError('Selecione a forma de pagamento.')
        self.estrategia.validar(valor, dados)
        return self.estrategia.descrever(valor, dados)


# A ordem define a ordem das opcoes na tela de baixa.
# Os codigos sao os mesmos de FORMA_CHOICES nos models de baixa.
ESTRATEGIAS = {
    estrategia.codigo: estrategia
    for estrategia in (
        PagamentoDinheiro(),
        PagamentoSimples('pix', 'PIX', '💠'),
        PagamentoSimples('cartao_debito', 'Cartão de Débito', '💳'),
        PagamentoCartaoCredito(),
        PagamentoSimples('transferencia', 'Transferência', '🏦'),
        PagamentoSimples('boleto', 'Boleto', '📄'),
        PagamentoCheque(),
    )
}


def obter_estrategia(codigo) -> EstrategiaPagamento:
    try:
        return ESTRATEGIAS[codigo]
    except KeyError as exc:
        raise ValueError('Forma de pagamento inválida.') from exc


def formas_pagamento():
    return list(ESTRATEGIAS.values())
