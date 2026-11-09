"""Padrao Template Method: exportacao de relatorios.

exportar() define o algoritmo fixo:
    validar -> cabecalho -> linhas (com separador) -> rodape -> resposta HTTP
As subclasses implementam so as etapas que mudam de formato para formato.
"""
import csv
import io
import json
from abc import ABC, abstractmethod
from typing import final

from django.http import HttpResponse
from django.utils import timezone


class ExportadorRelatorio(ABC):
    content_type = ''
    extensao = ''

    @final
    def exportar(self, dados, nome_arquivo: str) -> HttpResponse:
        """Template method. Marcado com @final: subclasses não mudam a ordem das etapas."""
        self._validar(dados)
        partes = [self.cabecalho(dados)]
        for indice, linha in enumerate(dados.linhas):
            if indice > 0:
                partes.append(self.separador_entre_linhas())
            partes.append(self.linha(dados.colunas, linha))
        partes.append(self.rodape(dados))
        return self._resposta(''.join(partes), nome_arquivo)

    # ---- Etapas abstratas: cada formato implementa ----

    @abstractmethod
    def cabecalho(self, dados) -> str:
        ...

    @abstractmethod
    def linha(self, colunas, valores) -> str:
        ...

    # ---- Hooks: comportamento padrão que pode ser sobrescrito ----

    def separador_entre_linhas(self) -> str:
        return ''

    def rodape(self, dados) -> str:
        return ''

    # ---- Etapas comuns a todos os formatos ----

    @staticmethod
    def _validar(dados):
        quantidade = len(dados.colunas)
        for linha in dados.linhas:
            if len(linha) != quantidade:
                raise ValueError('Cada linha do relatório deve ter um valor por coluna.')

    def _resposta(self, conteudo, nome_arquivo):
        response = HttpResponse(conteudo, content_type=self.content_type)
        response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}.{self.extensao}"'
        return response


class ExportadorCSV(ExportadorRelatorio):
    """CSV separado por ';' (padrão do Excel em português)."""

    content_type = 'text/csv; charset=utf-8'
    extensao = 'csv'
    BOM_UTF8 = '﻿'  # faz o Excel abrir o arquivo como UTF-8

    @staticmethod
    def _linha_csv(valores):
        buffer = io.StringIO()
        csv.writer(buffer, delimiter=';').writerow(valores)
        return buffer.getvalue()

    def cabecalho(self, dados):
        return self.BOM_UTF8 + self._linha_csv(dados.colunas)

    def linha(self, colunas, valores):
        return self._linha_csv(valores)


class ExportadorJSON(ExportadorRelatorio):
    content_type = 'application/json; charset=utf-8'
    extensao = 'json'

    def cabecalho(self, dados):
        titulo = json.dumps(dados.titulo, ensure_ascii=False)
        gerado_em = json.dumps(timezone.localtime().isoformat(timespec='seconds'))
        return f'{{"titulo": {titulo}, "gerado_em": {gerado_em}, "registros": ['

    def linha(self, colunas, valores):
        return json.dumps(dict(zip(colunas, valores)), ensure_ascii=False)

    def separador_entre_linhas(self):
        return ', '

    def rodape(self, dados):
        return f'], "total": {len(dados.linhas)}}}'


EXPORTADORES = {
    'csv': ExportadorCSV,
    'json': ExportadorJSON,
}


def obter_exportador(formato):
    exportador = EXPORTADORES.get(formato)
    return exportador() if exportador else None
