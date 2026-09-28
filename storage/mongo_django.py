"""Backend Django Storage que grava ImageField/FileField no GridFS."""
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage

from .manager import StorageManager
from .service import ArquivoService


class MongoGridFSStorage(Storage):
    def _service(self):
        return ArquivoService(StorageManager.get_instance().get_mongo_adapter())

    def _open(self, name, mode="rb"):
        return ContentFile(self._service().buscar(name), name=name)

    def _save(self, name, content):
        chunks = []
        for chunk in content.chunks():
            chunks.append(chunk)
        return self._service().salvar(name, b"".join(chunks))

    def delete(self, name):
        self._service().excluir(name)

    def exists(self, name):
        return self._service().existe(name)

    def url(self, name):
        return f"{settings.MEDIA_URL.rstrip('/')}/gridfs/{name}"
