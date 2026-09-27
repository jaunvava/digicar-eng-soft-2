import mimetypes

from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET

from .factory import criar_storage


@require_GET
def servir_gridfs(request, identificador):
    try:
        conteudo = criar_storage().buscar(identificador)
    except (FileNotFoundError, ValueError):
        raise Http404("Arquivo não encontrado")
    tipo, _ = mimetypes.guess_type(identificador)
    return HttpResponse(conteudo, content_type=tipo or "application/octet-stream")
