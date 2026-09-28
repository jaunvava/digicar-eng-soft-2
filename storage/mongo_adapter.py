from io import BytesIO

from bson import ObjectId
from bson.errors import InvalidId
from gridfs import GridFS
from gridfs.errors import NoFile
from pymongo import MongoClient

from .interfaces import ArquivoStorage


class MongoStorageAdapter(ArquivoStorage):
    """Adapta o pymongo/GridFS para a interface ArquivoStorage."""

    def __init__(
        self,
        client: MongoClient,
        database_name: str = "digicar",
    ):
        self.client = client
        self.database = self.client[database_name]
        self.fs = GridFS(self.database)

    def conectar(self) -> None:
        # Falha logo se o MongoDB estiver indisponivel.
        self.client.admin.command("ping")

    def desconectar(self) -> None:
        # O MongoClient e compartilhado pelo StorageManager e mantem um pool:
        # a conexao volta ao pool sozinha e o client nao pode ser fechado aqui,
        # pois um MongoClient fechado nao pode ser reutilizado.
        pass

    def salvar(self, nome: str, conteudo: bytes) -> str:

        arquivo_id = self.fs.put(
            BytesIO(conteudo),
            filename=nome
        )

        return str(arquivo_id)

    def buscar(self, identificador: str) -> bytes:
        try:
            arquivo = self.fs.get(ObjectId(identificador))
        except (InvalidId, NoFile) as exc:
            raise FileNotFoundError(f"Arquivo não encontrado: {identificador}") from exc
        return arquivo.read()

    def excluir(self, identificador: str) -> None:
        try:
            arquivo_id = ObjectId(identificador)
        except InvalidId:
            # Mesmo contrato do adapter local: excluir o que nao existe nao falha.
            return

        self.fs.delete(arquivo_id)

    def existe(self, identificador: str) -> bool:

        try:
            self.fs.get(
                ObjectId(identificador)
            )

            return True

        except (InvalidId, NoFile):
            return False
