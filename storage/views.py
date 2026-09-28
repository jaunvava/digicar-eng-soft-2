import mimetypes

from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET

from .manager import StorageManager
from .service import ArquivoService


@require_GET
def servir_gridfs(request, identificador):
    try:
        conteudo = ArquivoService(StorageManager.get_instance().get_mongo_adapter()).buscar(identificador)
    except (FileNotFoundError, ValueError):
        raise Http404("Arquivo não encontrado")
    tipo, _ = mimetypes.guess_type(identificador)
    return HttpResponse(conteudo, content_type=tipo or "application/octet-stream")
