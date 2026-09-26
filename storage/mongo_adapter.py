from io import BytesIO

from bson import ObjectId
from gridfs import GridFS
from pymongo import MongoClient

from .interface import ArquivoStorage


class MongoStorageAdapter(ArquivoStorage):

    def __init__(
        self,
        connection_string: str,
        database_name: str = "digicar"
    ):
        self.client = MongoClient(connection_string)
        self.database = self.client[database_name]
        self.fs = GridFS(self.database)

    def salvar(self, nome: str, conteudo: bytes) -> str:

        arquivo_id = self.fs.put(
            BytesIO(conteudo),
            filename=nome
        )

        return str(arquivo_id)

    def buscar(self, identificador: str) -> bytes:

        arquivo = self.fs.get(
            ObjectId(identificador)
        )

        return arquivo.read()

    def excluir(self, identificador: str) -> None:

        self.fs.delete(
            ObjectId(identificador)
        )

    def existe(self, identificador: str) -> bool:

        try:
            self.fs.get(
                ObjectId(identificador)
            )

            return True

        except Exception:
            return False