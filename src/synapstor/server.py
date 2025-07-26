from synapstor.mcp_server import QdrantMCPServer
from synapstor.settings import (
    EmbeddingProviderSettings,
    QdrantSettings,
    ToolSettings,
    I18nSettings,
)

mcp = QdrantMCPServer(
    tool_settings=ToolSettings(),
    qdrant_settings=QdrantSettings(),
    embedding_provider_settings=EmbeddingProviderSettings(),
    i18n_settings=I18nSettings(),
)
