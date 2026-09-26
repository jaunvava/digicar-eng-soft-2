import os

from .local_adapter import LocalStorageAdapter
from .mongo_adapter import MongoStorageAdapter


def criar_storage():

    tipo = os.environ.get(
        "FILE_STORAGE",
        "local"
    )

    if( tipo == "mongo"):

        return MongoStorageAdapter(
            connection_string=os.environ.get(
                "MONGO_URI",
                "mongodb://localhost:27017"
            ),
            database_name=os.environ.get(
                "MONGO_DATABASE",
                "digicar"
            )
        )

    return LocalStorageAdapter()