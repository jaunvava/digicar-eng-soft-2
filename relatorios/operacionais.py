"""Padrao Factory Method: relatorios operacionais.

Produto  -> RelatorioOperacional (clientes, veiculos, estoque, ordens)
Criador  -> RelatorioCreator, cujo factory method criar_relatorio() e
            implementado por cada criador concreto.

A view pede o criador pelo tipo e chama montar(); ela nao conhece as classes
concretas. Um relatorio novo e um par produto/criador registrado em CRIADORES.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from clientes.models import Cliente, Veiculo
from core.formatacao import formatar_moeda, formatar_quantidade
from ordens.models import OrdemServico
from produtos.models import Produto


@dataclass(frozen=True)
class DadosRelatorio:
    titulo: str
    colunas: list
    linhas: list


# ---- Produtos ----

class RelatorioOperacional(ABC):
    titulo = ''
    colunas = []

    @abstractmethod
    def consultar(self, empresa):
        """Queryset com os registros da empresa."""

    @abstractmethod
    def linha(self, registro) -> list:
        """Valores (texto) de uma linha, na ordem de colunas."""


class RelatorioClientes(RelatorioOperacional):
    titulo = 'Relatório de Clientes'
    colunas = ['Nome', 'Documento', 'Telefone', 'Cidade', 'Status']

    def consultar(self, empresa):
        return Cliente.objects.filter(empresa=empresa).order_by('nome')

    def linha(self, cliente):
        return [
            cliente.nome,
            cliente.cpf_cnpj or '—',
            cliente.telefone or '—',
            cliente.cidade or '—',
            'Ativo' if cliente.ativo else 'Inativo',
        ]


class RelatorioVeiculos(RelatorioOperacional):
    titulo = 'Relatório de Veículos'
    colunas = ['Placa', 'Veículo', 'Cliente', 'Chassi']

    def consultar(self, empresa):
        return Veiculo.objects.filter(cliente__empresa=empresa).select_related('cliente')

    def linha(self, veiculo):
        return [
            veiculo.placa,
            f'{veiculo.marca} {veiculo.modelo}'.strip(),
            veiculo.cliente.nome,
            veiculo.chassi or '—',
        ]


class RelatorioEstoque(RelatorioOperacional):
    titulo = 'Relatório de Estoque'
    colunas = ['Produto', 'Código', 'Atual', 'Mínimo', 'Situação']

    def consultar(self, empresa):
        return Produto.objects.filter(empresa=empresa, tipo='produto').order_by('nome')

    def linha(self, produto):
        return [
            produto.nome,
            produto.codigo or '—',
            f'{formatar_quantidade(produto.estoque_atual)} {produto.unidade}',
            formatar_quantidade(produto.estoque_minimo),
            'Baixo' if produto.estoque_baixo else 'Normal',
        ]


class RelatorioOrdens(RelatorioOperacional):
    titulo = 'Relatório de Ordens de Serviço'
    colunas = ['Número', 'Cliente', 'Veículo', 'Status', 'Total']

    def consultar(self, empresa):
        return OrdemServico.objects.filter(empresa=empresa).select_related('cliente', 'veiculo')

    def linha(self, ordem):
        return [
            f'#{ordem.numero}',
            ordem.cliente.nome,
            ordem.veiculo.placa if ordem.veiculo else '—',
            ordem.get_status_display(),
            formatar_moeda(ordem.total),
        ]


# ---- Criadores ----

class RelatorioCreator(ABC):

    @abstractmethod
    def criar_relatorio(self) -> RelatorioOperacional:
        """Factory method: cada criador decide qual relatório instanciar."""

    def montar(self, empresa) -> DadosRelatorio:
        relatorio = self.criar_relatorio()
        linhas = [relatorio.linha(registro) for registro in relatorio.consultar(empresa)]
        return DadosRelatorio(relatorio.titulo, list(relatorio.colunas), linhas)


class ClientesCreator(RelatorioCreator):
    def criar_relatorio(self):
        return RelatorioClientes()


class VeiculosCreator(RelatorioCreator):
    def criar_relatorio(self):
        return RelatorioVeiculos()


class EstoqueCreator(RelatorioCreator):
    def criar_relatorio(self):
        return RelatorioEstoque()


class OrdensCreator(RelatorioCreator):
    def criar_relatorio(self):
        return RelatorioOrdens()


CRIADORES = {
    'clientes': ClientesCreator,
    'veiculos': VeiculosCreator,
    'estoque': EstoqueCreator,
    'ordens': OrdensCreator,
}


def obter_criador(tipo):
    """Devolve o criador do tipo pedido, ou None se o tipo não existir."""
    criador = CRIADORES.get(tipo)
    return criador() if criador else None
