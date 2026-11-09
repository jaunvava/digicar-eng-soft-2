from django.http import HttpResponseForbidden


class RolePermissionMiddleware:
    """Aplica as regras de perfil também fora da interface HTML."""

    ADMIN_ROUTES = ('/configuracoes/', '/relatorios/')
    MANAGER_ROUTES = ('/clientes/', '/produtos/', '/fornecedores/', '/financeiro/', '/orcamentos/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                perfil = request.user.perfil
                path = request.path
                if any(path.startswith(route) for route in self.ADMIN_ROUTES) and perfil.perfil not in ('admin', 'gerente'):
                    return HttpResponseForbidden('Seu perfil não possui acesso a esta área.')
                if path.startswith('/configuracoes/') and perfil.perfil != 'admin':
                    return HttpResponseForbidden('Apenas administradores podem alterar configurações.')
                if path.endswith('/excluir/') and perfil.perfil not in ('admin', 'gerente'):
                    return HttpResponseForbidden('Apenas administradores e gerentes podem excluir registros.')
                if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                    if any(path.startswith(route) for route in self.MANAGER_ROUTES) and perfil.perfil == 'operador':
                        return HttpResponseForbidden('Seu perfil pode consultar esta área, mas não alterá-la.')
            except Exception:
                pass
        return self.get_response(request)
