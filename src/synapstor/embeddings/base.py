from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Classe base abstrata para provedores de embeddings."""

    @abstractmethod
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Converte uma lista de documentos em vetores."""
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """Converte uma consulta em vetor."""
        pass

    @abstractmethod
    def get_vector_name(self) -> str:
        """Obtém o nome do vetor para a coleção Qdrant."""
        pass

    @abstractmethod
    def get_vector_size(self) -> int:
        """Obtém o tamanho do vetor para a coleção Qdrant."""
        pass
