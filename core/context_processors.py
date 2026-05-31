def empresa_context(request):
    """Disponibiliza a empresa do tenant em todos os templates."""
    empresa = getattr(request, 'empresa', None)
    return {'empresa': empresa}
