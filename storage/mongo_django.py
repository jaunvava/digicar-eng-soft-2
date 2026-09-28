"""Backend Django Storage que grava ImageField/FileField no GridFS."""
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage

from .manager import StorageManager


class MongoGridFSStorage(Storage):
    def _adapter(self):
        return StorageManager.get_instance().get_mongo_adapter()

    def _open(self, name, mode="rb"):
        return ContentFile(self._adapter().buscar(name), name=name)

    def _save(self, name, content):
        chunks = []
        for chunk in content.chunks():
            chunks.append(chunk)
        return self._adapter().salvar(name, b"".join(chunks))

    def delete(self, name):
        self._adapter().excluir(name)

    def exists(self, name):
        return self._adapter().existe(name)

    def url(self, name):
        return f"{settings.MEDIA_URL.rstrip('/')}/gridfs/{name}"
