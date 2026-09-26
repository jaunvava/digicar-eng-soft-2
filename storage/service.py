from .factory import criar_storage


class ArquivoService:

    def __init__(self):
        self.storage = criar_storage()

    def salvar(
        self,
        nome: str,
        conteudo: bytes
    ) -> str:

        return self.storage.salvar(
            nome,
            conteudo
        )

    def buscar(
        self,
        identificador: str
    ) -> bytes:

        return self.storage.buscar(
            identificador
        )

    def excluir(
        self,
        identificador: str
    ) -> None:

        self.storage.excluir(
            identificador
        )

    def existe(
        self,
        identificador: str
    ) -> bool:

        return self.storage.existe(
            identificador
        )