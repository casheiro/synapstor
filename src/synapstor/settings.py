from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

from synapstor.embeddings.types import EmbeddingProviderType

DEFAULT_TOOL_STORE_DESCRIPTION = (
    "Guarde a memória para uso posterior, quando você for solicitado a lembrar algo."
)
DEFAULT_TOOL_FIND_DESCRIPTION = (
    "Busque memórias no Qdrant. Use esta ferramenta quando precisar: \n"
    " - Encontrar memórias pelo seu conteúdo \n"
    " - Acessar memórias para análise adicional \n"
    " - Obter algumas informações pessoais sobre o usuário"
)


class ToolSettings(BaseSettings):
    """
    Configuração para todas as ferramentas.
    """

    tool_store_description: str = Field(
        default=DEFAULT_TOOL_STORE_DESCRIPTION,
        validation_alias="TOOL_STORE_DESCRIPTION",
    )
    tool_find_description: str = Field(
        default=DEFAULT_TOOL_FIND_DESCRIPTION,
        validation_alias="TOOL_FIND_DESCRIPTION",
    )


class EmbeddingProviderSettings(BaseSettings):
    """
    Configuração para o provedor de embeddings.
    """

    provider_type: EmbeddingProviderType = Field(
        default=EmbeddingProviderType.FASTEMBED,
        validation_alias="EMBEDDING_PROVIDER",
    )
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL",
    )


class QdrantSettings(BaseSettings):
    """
    Configuração para o conector Qdrant.
    """

    location: Optional[str] = Field(default=None, validation_alias="QDRANT_URL")
    api_key: Optional[str] = Field(default=None, validation_alias="QDRANT_API_KEY")
    collection_name: Optional[str] = Field(
        default=None, validation_alias="COLLECTION_NAME"
    )
    local_path: Optional[str] = Field(
        default=None, validation_alias="QDRANT_LOCAL_PATH"
    )
    search_limit: Optional[int] = Field(
        default=None, validation_alias="QDRANT_SEARCH_LIMIT"
    )
    read_only: bool = Field(default=False, validation_alias="QDRANT_READ_ONLY")

    def get_qdrant_location(self) -> Optional[str]:
        """
        Obtém a localização do Qdrant, seja a URL ou o caminho local.
        """
        return self.location or self.local_path
