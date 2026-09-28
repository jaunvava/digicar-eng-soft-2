from pathlib import Path

from .interfaces import ArquivoStorage


class LocalStorageAdapter(ArquivoStorage):
    """Adapta o sistema de arquivos (pathlib) para a interface ArquivoStorage."""

    def __init__(self, base_path):
        self.base_path = Path(base_path).resolve()

    def _caminho(self, identificador: str) -> Path:
        caminho = (self.base_path / identificador).resolve()
        if not caminho.is_relative_to(self.base_path):
            raise ValueError("Identificador de arquivo inválido")
        return caminho

    def conectar(self) -> None:
        self.base_path.mkdir(
            parents=True,
            exist_ok=True
        )

    def desconectar(self) -> None:
        # O sistema de arquivos nao mantem conexao aberta.
        pass

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
