"""Conversao e formatacao de valores no padrao brasileiro."""
from decimal import Decimal, InvalidOperation


def converter_valor(texto) -> Decimal:
    """Aceita '1234.56' (campo com mascara) e '1.234,56' (digitado)."""
    if texto is None or str(texto).strip() == '':
        raise ValueError('Informe um valor.')
    texto = str(texto).strip().replace('R$', '').strip()
    if ',' in texto:
        texto = texto.replace('.', '').replace(',', '.')
    try:
        return Decimal(texto)
    except InvalidOperation as exc:
        raise ValueError(f'Valor inválido: {texto}') from exc


def formatar_moeda(valor) -> str:
    texto = f'{Decimal(valor):,.2f}'
    return 'R$ ' + texto.replace(',', '_').replace('.', ',').replace('_', '.')


def formatar_quantidade(valor) -> str:
    """10.000 -> '10'; 2.500 -> '2,5'."""
    texto = f'{Decimal(valor).normalize():f}'
    return texto.replace('.', ',')
