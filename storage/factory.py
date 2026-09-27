from threading import RLock

from django.conf import settings

from .local_adapter import LocalStorageAdapter
from .mongo_adapter import MongoStorageAdapter


def criar_storage():
    """Retorna uma unica instancia por configuracao, com inicializacao sincronizada."""
    global _instancia, _configuracao
    tipo = settings.FILE_STORAGE
    configuracao = (tipo, getattr(settings, "MONGO_URI", None), getattr(settings, "MONGO_DATABASE", None), str(getattr(settings, "MEDIA_ROOT", "")))
    with _lock:
        if _instancia is not None and _configuracao == configuracao:
            return _instancia
        if _instancia is not None and hasattr(_instancia, "close"):
            _instancia.close()
        if tipo == "mongo":
            _instancia = MongoStorageAdapter(connection_string=settings.MONGO_URI, database_name=settings.MONGO_DATABASE)
        elif tipo == "local":
            _instancia = LocalStorageAdapter()
        else:
            raise ValueError("FILE_STORAGE inválido. Use 'local' ou 'mongo'.")
        _configuracao = configuracao
        return _instancia


def _limpar_storage():
    global _instancia, _configuracao
    with _lock:
        if _instancia is not None and hasattr(_instancia, "close"):
            _instancia.close()
        _instancia = _configuracao = None


_lock = RLock()
_instancia = None
_configuracao = None
# Mantem compatibilidade com integracoes e testes que limpavam o cache LRU.
criar_storage.cache_clear = _limpar_storage
