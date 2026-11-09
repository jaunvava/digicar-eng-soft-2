from digicar import __version__


def empresa_context(request):
    """Disponibiliza a empresa do tenant e a versão do sistema em todos os templates."""
    empresa = getattr(request, 'empresa', None)
    return {'empresa': empresa, 'versao_sistema': __version__}
