"""Backend Django Storage que grava ImageField/FileField no GridFS."""
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage

from .factory import criar_storage


class MongoGridFSStorage(Storage):
    def _open(self, name, mode="rb"):
        return ContentFile(criar_storage().buscar(name), name=name)

    def _save(self, name, content):
        chunks = []
        for chunk in content.chunks():
            chunks.append(chunk)
        return criar_storage().salvar(name, b"".join(chunks))

    def delete(self, name):
        criar_storage().excluir(name)

    def exists(self, name):
        return criar_storage().existe(name)

    def url(self, name):
        return f"{settings.MEDIA_URL.rstrip('/')}/gridfs/{name}"
