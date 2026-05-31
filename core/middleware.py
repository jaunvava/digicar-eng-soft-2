class TenantMiddleware:
    """
    Middleware multi-tenant: injeta request.empresa com base no perfil do usuário logado.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.empresa = None
        if request.user.is_authenticated:
            try:
                request.empresa = request.user.perfil.empresa
            except Exception:
                pass
        response = self.get_response(request)
        return response
