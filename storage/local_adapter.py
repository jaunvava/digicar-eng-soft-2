from pathlib import Path

from django.conf import settings

from .interfaces import ArquivoStorage


class LocalStorageAdapter(ArquivoStorage):

    def __init__(self):
        self.base_path = Path(settings.MEDIA_ROOT).resolve()

    def _caminho(self, identificador: str) -> Path:
        caminho = (self.base_path / identificador).resolve()
        if not caminho.is_relative_to(self.base_path):
            raise ValueError("Identificador de arquivo inválido")
        return caminho

    def salvar(self, nome: str, conteudo: bytes) -> str:
        caminho = self._caminho(nome)

        caminho.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        caminho.write_bytes(conteudo)

        return nome

    def buscar(self, identificador: str) -> bytes:
        caminho = self._caminho(identificador)

        if (not caminho.exists()):
            raise FileNotFoundError(
                f"Arquivo nao encontrado: {identificador}"
            )

        return caminho.read_bytes()

    def excluir(self, identificador: str) -> None:
        caminho = self._caminho(identificador)

        if (caminho.exists()):
            caminho.unlink()

    def existe(self, identificador: str) -> bool:
        caminho = self._caminho(identificador)

        return caminho.exists()