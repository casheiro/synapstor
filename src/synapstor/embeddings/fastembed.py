import asyncio
from typing import List

from fastembed import TextEmbedding
from fastembed.common.model_description import DenseModelDescription

from synapstor.embeddings.base import EmbeddingProvider


class FastEmbedProvider(EmbeddingProvider):
    """
    Implementação do provedor de embeddings usando FastEmbed.
    :param model_name: O nome do modelo FastEmbed a ser usado.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embedding_model = TextEmbedding(model_name)

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Converte uma lista de documentos em vetores."""
        # Executa em uma thread pool já que o FastEmbed é síncrono
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(self.embedding_model.passage_embed(documents))
        )
        return [embedding.tolist() for embedding in embeddings]

    async def embed_query(self, query: str) -> List[float]:
        """Converte uma consulta em vetor."""
        # Executa em uma thread pool já que o FastEmbed é síncrono
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(self.embedding_model.query_embed([query]))
        )
        return embeddings[0].tolist()

    def get_vector_name(self) -> str:
        """
        Retorna o nome do vetor para a coleção Qdrant.
        Importante: Isso é compatível com a lógica do FastEmbed usada antes da versão 0.6.0.
        """
        model_name = self.embedding_model.model_name.split("/")[-1].lower()
        return f"fast-{model_name}"

    def get_vector_size(self) -> int:
        """Obtém o tamanho do vetor para a coleção Qdrant."""
        model_description: DenseModelDescription = (
            self.embedding_model._get_model_description(self.model_name)
        )
        return model_description.dim
