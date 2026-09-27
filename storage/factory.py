from functools import lru_cache

from django.conf import settings

from .local_adapter import LocalStorageAdapter
from .mongo_adapter import MongoStorageAdapter


@lru_cache(maxsize=1)
def criar_storage():
    tipo = settings.FILE_STORAGE
    if tipo == "mongo":
        return MongoStorageAdapter(
            connection_string=settings.MONGO_URI,
            database_name=settings.MONGO_DATABASE,
        )

    if tipo == "local":
        return LocalStorageAdapter()

    raise ValueError("FILE_STORAGE inválido. Use 'local' ou 'mongo'.")