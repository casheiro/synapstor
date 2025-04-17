import json
import logging
from typing import List, Any

from mcp.server.fastmcp import Context, FastMCP

from synapstor.embeddings.factory import create_embedding_provider
from synapstor.qdrant import Entry, Metadata, QdrantConnector
from synapstor.settings import (
    EmbeddingProviderSettings,
    QdrantSettings,
    ToolSettings,
)

logger = logging.getLogger(__name__)


# FastMCP is an alternative interface for declaring the capabilities
# of the server. Its API is based on FastAPI.
class QdrantMCPServer(FastMCP):
    """
    Um servidor MCP para Qdrant.
    """

    def __init__(
        self,
        tool_settings: ToolSettings,
        qdrant_settings: QdrantSettings,
        embedding_provider_settings: EmbeddingProviderSettings,
        name: str = "synapstor",
        instructions: str | None = None,
        **settings: Any,
    ):
        self.tool_settings = tool_settings
        self.qdrant_settings = qdrant_settings
        self.embedding_provider_settings = embedding_provider_settings

        self.embedding_provider = create_embedding_provider(embedding_provider_settings)
        self.qdrant_connector = QdrantConnector(
            qdrant_settings.location,
            qdrant_settings.api_key,
            qdrant_settings.collection_name,
            self.embedding_provider,
            qdrant_settings.local_path,
        )

        super().__init__(name=name, instructions=instructions, **settings)

        self.setup_tools()

    def format_entry(self, entry: Entry) -> str:
        """
        Sinta-se à vontade para sobrescrever este método na sua subclasse para personalizar o formato da entrada.
        """
        entry_metadata = json.dumps(entry.metadata) if entry.metadata else ""
        return f"<entry><content>{entry.content}</content><metadata>{entry_metadata}</metadata></entry>"

    def setup_tools(self):
        async def store(
            ctx: Context,
            information: str,
            collection_name: str,
            # The `metadata` parameter is defined as non-optional, but it can be None.
            # If we set it to be optional, some of the MCP clients, like Cursor, cannot
            # handle the optional parameter correctly.
            metadata: Metadata = None,
        ) -> str:
            """
            Armazena algumas informações no Qdrant.
            :param ctx: O contexto para a requisição.
            :param information: A informação a ser armazenada.
            :param metadata: Metadados JSON para armazenar com a informação, opcional.
            :param collection_name: O nome da coleção para armazenar a informação, opcional. Se não fornecido,
                                    a coleção padrão é usada.
            :return: Uma mensagem indicando que a informação foi armazenada.
            """
            await ctx.debug(f"Armazenando informação {information} no Qdrant")

            entry = Entry(content=information, metadata=metadata)

            await self.qdrant_connector.store(entry, collection_name=collection_name)
            if collection_name:
                return f"Lembrado: {information} na coleção {collection_name}"
            return f"Lembrado: {information}"

        async def store_with_default_collection(
            ctx: Context,
            information: str,
            metadata: Metadata = None,
        ) -> str:
            return await store(
                ctx, information, self.qdrant_settings.collection_name, metadata
            )

        async def find(
            ctx: Context,
            query: str,
            collection_name: str,
        ) -> List[str]:
            """
            Encontra memórias no Qdrant.
            :param ctx: O contexto para a requisição.
            :param query: A consulta a ser usada para a busca.
            :param collection_name: O nome da coleção para buscar, opcional. Se não fornecido,
                                    a coleção padrão é usada.
            :param limit: O número máximo de entradas a retornar, opcional. O padrão é 10.
            :return: Uma lista de entradas encontradas.
            """
            await ctx.debug(f"Encontrando resultados para consulta {query}")
            if collection_name:
                await ctx.debug(f"Substituindo o nome da coleção por {collection_name}")

            entries = await self.qdrant_connector.search(
                query,
                collection_name=collection_name,
                limit=self.qdrant_settings.search_limit,
            )
            if not entries:
                return [f"Nenhuma informação encontrada para a consulta '{query}'"]
            content = [
                f"Resultados para a consulta '{query}'",
            ]
            for entry in entries:
                content.append(self.format_entry(entry))
            return content

        async def find_with_default_collection(
            ctx: Context,
            query: str,
        ) -> List[str]:
            return await find(ctx, query, self.qdrant_settings.collection_name)

        # Register the tools depending on the configuration

        if self.qdrant_settings.collection_name:
            self.add_tool(
                find_with_default_collection,
                name="qdrant-find",
                description=self.tool_settings.tool_find_description,
            )
        else:
            self.add_tool(
                find,
                name="qdrant-find",
                description=self.tool_settings.tool_find_description,
            )

        if not self.qdrant_settings.read_only:
            # Those methods can modify the database

            if self.qdrant_settings.collection_name:
                self.add_tool(
                    store_with_default_collection,
                    name="qdrant-store",
                    description=self.tool_settings.tool_store_description,
                )
            else:
                self.add_tool(
                    store,
                    name="qdrant-store",
                    description=self.tool_settings.tool_store_description,
                )

        # Carrega ferramentas adicionais dos plugins
        try:
            from synapstor.plugins import load_plugin_tools

            plugin_tools = load_plugin_tools(self)
            if plugin_tools:
                logger.info(
                    f"Ferramentas carregadas dos plugins: {', '.join(plugin_tools)}"
                )
        except Exception as e:
            logger.warning(f"Erro ao carregar plugins: {e}")
