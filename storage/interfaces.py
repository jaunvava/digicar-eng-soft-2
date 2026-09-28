from abc import ABC, abstractmethod

class ArquivoStorage(ABC):
    """Interface alvo (Target) do padrao Adapter para armazenamento de arquivos."""

    @abstractmethod
    def conectar(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def desconectar(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def salvar(self, nome: str, conteudo: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def buscar(self, identificador: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def excluir(self, identificador: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def existe(self, identificador: str) -> bool:
        raise NotImplementedError
