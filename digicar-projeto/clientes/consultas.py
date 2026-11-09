"""Consultas de clientes usadas pelos formulários (busca paginada e validação)."""
import re

from django.db.models import Q, Value
from django.db.models.functions import Replace

from .models import Cliente

POR_PAGINA = 20


def _sem_pontuacao(campo, caracteres):
    expressao = campo
    for caractere in caracteres:
        expressao = Replace(expressao, Value(caractere), Value(''))
    return expressao


def buscar_clientes(empresa, termo='', pagina=1, por_pagina=POR_PAGINA):
    """Clientes ativos da empresa que batem com o termo, uma página por vez.

    Busca por nome, CPF/CNPJ e telefones (com ou sem pontuação) e pelo código.
    Devolve (clientes, tem_mais).
    """
    qs = Cliente.objects.filter(empresa=empresa, ativo=True)
    termo = (termo or '').strip()
    if termo:
        filtro = Q(nome__icontains=termo) | Q(cpf_cnpj__icontains=termo) | Q(email__icontains=termo)
        digitos = re.sub(r'\D', '', termo)
        if len(digitos) >= 3:
            qs = qs.annotate(
                _doc=_sem_pontuacao('cpf_cnpj', '.-/ '),
                _tel=_sem_pontuacao('telefone', '()- '),
                _cel=_sem_pontuacao('celular', '()- '),
            )
            filtro |= Q(_doc__contains=digitos) | Q(_tel__contains=digitos) | Q(_cel__contains=digitos)
        if termo.isdigit():
            filtro |= Q(pk=int(termo))
        qs = qs.filter(filtro)

    pagina = max(1, pagina)
    inicio = (pagina - 1) * por_pagina
    resultados = list(qs.order_by('nome', 'pk')[inicio:inicio + por_pagina + 1])
    return resultados[:por_pagina], len(resultados) > por_pagina


def cliente_da_empresa(empresa, valor, permitir=None):
    """Valida o cliente enviado por um formulário.

    Só aceita clientes ativos da empresa. `permitir` é o pk que pode ser
    mantido mesmo inativo (o cliente atual de um registro em edição).
    Levanta ValueError com mensagem para o usuário.
    """
    try:
        pk = int(valor)
    except (TypeError, ValueError):
        raise ValueError('Selecione um cliente da lista.') from None
    filtro = Q(ativo=True)
    if permitir:
        filtro |= Q(pk=permitir)
    cliente = Cliente.objects.filter(filtro, empresa=empresa, pk=pk).first()
    if cliente is None:
        raise ValueError('Cliente inválido ou inativo. Selecione um cliente da lista.')
    return cliente


def cliente_json(cliente):
    detalhes = [parte for parte in (
        cliente.cpf_cnpj,
        cliente.celular or cliente.telefone,
        f'{cliente.cidade}/{cliente.estado}' if cliente.cidade else '',
    ) if parte]
    return {'id': cliente.pk, 'nome': cliente.nome, 'detalhe': ' · '.join(detalhes)}
