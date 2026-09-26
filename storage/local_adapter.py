from pathlib import Path

from django.conf import settings

from .interface import ArquivoStorage


class LocalStorageAdapter(ArquivoStorage):

    def __init__(self):
        self.base_path = Path(settings.MEDIA_ROOT)

    def salvar(self, nome: str, conteudo: bytes) -> str:
        caminho = self.base_path / nome

        caminho.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        caminho.write_bytes(conteudo)

        return nome

    def buscar(self, identificador: str) -> bytes:
        caminho = self.base_path / identificador

        if (not caminho.exists()):
            raise FileNotFoundError(
                f"Arquivo nao encontrado: {identificador}"
            )

        return caminho.read_bytes()

    def excluir(self, identificador: str) -> None:
        caminho = self.base_path / identificador

        if (caminho.exists()):
            caminho.unlink()

    def existe(self, identificador: str) -> bool:
        caminho = self.base_path / identificador

        return caminho.exists()