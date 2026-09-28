from .interfaces import ArquivoStorage


class ArquivoService:
    """Cliente do padrao Adapter: conhece apenas a interface ArquivoStorage."""

    def __init__(self, storage: ArquivoStorage):
        self.storage = storage

    def _executar(self, operacao, *args):
        self.storage.conectar()
        try:
            return operacao(*args)
        finally:
            self.storage.desconectar()

    def salvar(
        self,
        nome: str,
        conteudo: bytes
    ) -> str:

        return self._executar(
            self.storage.salvar,
            nome,
            conteudo
        )

    def buscar(
        self,
        identificador: str
    ) -> bytes:

        return self._executar(
            self.storage.buscar,
            identificador
        )

    def excluir(
        self,
        identificador: str
    ) -> None:

        self._executar(
            self.storage.excluir,
            identificador
        )

    def existe(
        self,
        identificador: str
    ) -> bool:

        return self._executar(
            self.storage.existe,
            identificador
        )
