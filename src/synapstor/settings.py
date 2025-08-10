from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

from synapstor.embeddings.types import EmbeddingProviderType

DEFAULT_TOOL_STORE_DESCRIPTION = (
    "Store memory for later use, when you are asked to remember something."
)
DEFAULT_TOOL_FIND_DESCRIPTION = (
    "Search memories in Qdrant. Use this tool when you need: \n"
    " - Find memories by their content \n"
    " - Access memories for additional analysis \n"
    " - Get some personal information about the user"
)


class ToolSettings(BaseSettings):
    """
    Configuration for all tools.
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
    Configuration for the embedding provider.
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
    Configuration for the Qdrant connector.
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
        Gets the Qdrant location, either the URL or the local path.
        """
        return self.location or self.local_path


class ServerSettings(BaseSettings):
    """
    Configuration for the MCP server transport.
    """

    host: str = Field(default="0.0.0.0", validation_alias="MCP_SERVER_HOST")
    port: int = Field(default=8000, validation_alias="MCP_SERVER_PORT")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"], validation_alias="MCP_CORS_ORIGINS"
    )


class I18nSettings(BaseSettings):
    """
    Configuration for internationalization.
    """

    language: str = Field(default="en", validation_alias="SYNAPSTOR_LANGUAGE")
    auto_detect: bool = Field(
        default=True, validation_alias="SYNAPSTOR_AUTO_DETECT_LANGUAGE"
    )


class MEFSettings(BaseSettings):
    """
    Configuration for Matrix Embedding Framework (MEF).
    """

    enabled: bool = Field(default=False, validation_alias="MEF_ENABLED")
    enforce_structure: bool = Field(
        default=False, validation_alias="MEF_ENFORCE_STRUCTURE"
    )
    auto_detect: bool = Field(default=True, validation_alias="MEF_AUTO_DETECT")
    required_fields: list[str] = Field(
        default_factory=lambda: ["id", "title", "domain", "type", "content"],
        validation_alias="MEF_REQUIRED_FIELDS",
    )
    supported_domains: list[str] = Field(
        default_factory=lambda: [
            "product",
            "business",
            "technical",
            "strategy",
            "culture",
        ],
        validation_alias="MEF_SUPPORTED_DOMAINS",
    )
    supported_types: list[str] = Field(
        default_factory=lambda: [
            "business_rule",
            "function",
            "template",
            "guideline",
            "pattern",
            "decision",
            "example",
        ],
        validation_alias="MEF_SUPPORTED_TYPES",
    )
    supported_contexts: list[str] = Field(
        default_factory=lambda: [
            "discovery",
            "implementation",
            "refinement",
            "qa",
            "documentation",
            "support",
        ],
        validation_alias="MEF_SUPPORTED_CONTEXTS",
    )
