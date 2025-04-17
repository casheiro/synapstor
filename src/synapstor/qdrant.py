import logging
import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel
from qdrant_client import AsyncQdrantClient, models

from synapstor.embeddings.base import EmbeddingProvider

# Importa o gerador de IDs determinísticos
try:
    from synapstor.utils.id_generator import gerar_id_determinista
except ImportError:
    # Fallback caso ainda não exista o módulo
    import hashlib

    def gerar_id_determinista(metadata: Dict[str, Any]) -> str:
        """Versão interna de fallback do gerador de IDs determinísticos"""
        # Extrai dados para identificação
        projeto = metadata.get("projeto", "")
        caminho = metadata.get("caminho_absoluto", "")

        if projeto and caminho:
            content_hash = f"{projeto}:{caminho}"
        else:
            content_hash = ":".join(
                f"{k}:{v}" for k, v in sorted(metadata.items()) if v
            )

        if not content_hash:
            return uuid.uuid4().hex

        return hashlib.md5(content_hash.encode("utf-8")).hexdigest()


logger = logging.getLogger(__name__)

Metadata = Dict[str, Any]


class Entry(BaseModel):
    """
    Uma única entrada na coleção Qdrant.
    """

    content: str
    metadata: Optional[Metadata] = None


class QdrantConnector:
    """
    Encapsula a conexão com um servidor Qdrant e todos os métodos para interagir com ele.
    :param qdrant_url: A URL do servidor Qdrant.
    :param qdrant_api_key: A chave de API a ser usada para o servidor Qdrant.
    :param collection_name: O nome da coleção a ser usada.
    :param embedding_provider: O provedor de embeddings a ser usado.
    :param qdrant_local_path: O caminho para o diretório de armazenamento do cliente Qdrant, se o modo local for usado.
    """

    def __init__(
        self,
        qdrant_url: Optional[str],
        qdrant_api_key: Optional[str],
        collection_name: str,
        embedding_provider: EmbeddingProvider,
        qdrant_local_path: Optional[str] = None,
    ):
        self._qdrant_url = qdrant_url.rstrip("/") if qdrant_url else None
        self._qdrant_api_key = qdrant_api_key
        self._default_collection_name = collection_name
        self._embedding_provider = embedding_provider
        self._client = AsyncQdrantClient(
            location=qdrant_url, api_key=qdrant_api_key, path=qdrant_local_path
        )

    async def get_collection_names(self) -> list[str]:
        """
        Obtém os nomes de todas as coleções no servidor Qdrant.
        :return: Uma lista de nomes de coleções.
        """
        response = await self._client.get_collections()
        return [collection.name for collection in response.collections]

    async def store(self, entry: Entry, *, collection_name: Optional[str] = None):
        """
        Armazena informações na coleção Qdrant, junto com os metadados especificados.
        :param entry: A entrada a ser armazenada na coleção Qdrant.
        :param collection_name: O nome da coleção para armazenar as informações, opcional. Se não fornecido,
                                a coleção padrão é usada.
        """
        collection_name = collection_name or self._default_collection_name
        await self._ensure_collection_exists(collection_name)

        # Embed the document
        # ToDo: instead of embedding text explicitly, use `models.Document`,
        # it should unlock usage of server-side inference.
        embeddings = await self._embedding_provider.embed_documents([entry.content])

        # Add to Qdrant
        vector_name = self._embedding_provider.get_vector_name()
        payload = {"document": entry.content, "metadata": entry.metadata}

        # Gera um ID determinístico se houver metadados suficientes
        if entry.metadata:
            # Usa o gerador de IDs determinísticos
            document_id = gerar_id_determinista(entry.metadata)
        else:
            # Fallback para UUID se não tiver metadados
            document_id = uuid.uuid4().hex

        # Log informativo
        logger.debug(f"Armazenando documento com ID: {document_id}")

        await self._client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=document_id,  # Usa ID determinístico ou UUID
                    vector={vector_name: embeddings[0]},
                    payload=payload,
                )
            ],
        )

    async def search(
        self, query: str, *, collection_name: Optional[str] = None, limit: int = 10
    ) -> list[Entry]:
        """
        Encontra pontos na coleção Qdrant. Se não houver entradas encontradas, uma lista vazia é retornada.
        :param query: A consulta a ser usada para a busca.
        :param collection_name: O nome da coleção para pesquisar, opcional. Se não fornecido,
                                a coleção padrão é usada.
        :param limit: O número máximo de entradas a retornar.
        :return: Uma lista de entradas encontradas.
        """
        collection_name = collection_name or self._default_collection_name
        collection_exists = await self._client.collection_exists(collection_name)
        if not collection_exists:
            return []

        # Embed the query
        # ToDo: instead of embedding text explicitly, use `models.Document`,
        # it should unlock usage of server-side inference.

        query_vector = await self._embedding_provider.embed_query(query)
        vector_name = self._embedding_provider.get_vector_name()

        # Search in Qdrant
        search_results = await self._client.query_points(
            collection_name=collection_name,
            query=query_vector,
            using=vector_name,
            limit=limit,
        )

        return [
            Entry(
                content=result.payload["document"],
                metadata=result.payload.get("metadata"),
            )
            for result in search_results.points
        ]

    async def _ensure_collection_exists(self, collection_name: str):
        """
        Garante que a coleção existe, criando-a se necessário.
        :param collection_name: O nome da coleção para garantir que existe.
        """
        collection_exists = await self._client.collection_exists(collection_name)
        if not collection_exists:
            # Create the collection with the appropriate vector size
            vector_size = self._embedding_provider.get_vector_size()

            # Use the vector name as defined in the embedding provider
            vector_name = self._embedding_provider.get_vector_name()
            await self._client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    vector_name: models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    )
                },
            )
