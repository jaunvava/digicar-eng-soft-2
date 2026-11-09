from threading import Lock

from django.conf import settings
from pymongo import MongoClient

from .local_adapter import LocalStorageAdapter
from .mongo_adapter import MongoStorageAdapter


class StorageManager:
    """Singleton que guarda os adapters de armazenamento de arquivos."""

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        # Equivalente ao construtor privado: a unica forma de obter o objeto e get_instance().
        raise TypeError("Use StorageManager.get_instance()")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instancia = super().__new__(cls)
                    mongo_client = MongoClient(settings.MONGO_URI)

                    instancia._local_adapter = LocalStorageAdapter(settings.MEDIA_ROOT)
                    instancia._mongo_adapter = MongoStorageAdapter(
                        mongo_client,
                        database_name=settings.MONGO_DATABASE,
                    )
                    cls._instance = instancia
        return cls._instance

    def get_local_adapter(self):
        return self._local_adapter

    def get_mongo_adapter(self):
        return self._mongo_adapter

    def get_adapter_configurado(self):
        """Devolve o adapter escolhido em FILE_STORAGE."""
        if settings.FILE_STORAGE == "mongo":
            return self._mongo_adapter
        if settings.FILE_STORAGE == "local":
            return self._local_adapter
        raise ValueError("FILE_STORAGE inválido. Use 'local' ou 'mongo'.")
