from abc import ABC, abstractmethod

class ArquivoStorage(ABC):

    @abstractmethod
    def salvar(self, nome: str, conteudo: bytes) -> str:
        pass

    @abstractmethod
    def buscar(self, identificador: str) -> bytes:
        pass

    @abstractmethod
    def excluir(self, identificador: str) -> None:
        pass

    @abstractmethod
    def existe(self, identificador: str) -> bool:
        pass