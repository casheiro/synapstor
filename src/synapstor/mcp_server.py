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
    I18nSettings,
)
from synapstor.i18n import get_translator, set_language, SupportedLanguages

logger = logging.getLogger(__name__)


# FastMCP is an alternative interface for declaring the capabilities
# of the server. Its API is based on FastAPI.
class QdrantMCPServer(FastMCP):
    """
    An MCP server for Qdrant.
    """

    def __init__(
        self,
        tool_settings: ToolSettings,
        qdrant_settings: QdrantSettings,
        embedding_provider_settings: EmbeddingProviderSettings,
        i18n_settings: I18nSettings | None = None,
        name: str = "synapstor",
        instructions: str | None = None,
        **settings: Any,
    ):
        self.tool_settings = tool_settings
        self.qdrant_settings = qdrant_settings
        self.embedding_provider_settings = embedding_provider_settings
        self.i18n_settings = i18n_settings or I18nSettings()
        
        # Configurar idioma
        language = SupportedLanguages.get_language_by_code(self.i18n_settings.language)
        set_language(language)

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
        Feel free to override this method in your subclass to customize the entry format.
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
            Store some information in Qdrant.
            :param ctx: The context for the request.
            :param information: The information to store.
            :param metadata: JSON metadata to store with the information, optional.
            :param collection_name: The collection name to store the information in, optional. If not provided,
                                    the default collection is used.
            :return: A message indicating that the information has been stored.
            """
            await ctx.debug(f"Storing information {information} in Qdrant")

            entry = Entry(content=information, metadata=metadata)

            await self.qdrant_connector.store(entry, collection_name=collection_name)
            translator = get_translator()
            if collection_name:
                return translator.translate("tools.store.success_with_collection", 
                                          information=information, 
                                          collection_name=collection_name)
            return translator.translate("tools.store.success", information=information)

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
            Find memories in Qdrant.
            :param ctx: The context for the request.
            :param query: The query to use for the search.
            :param collection_name: The collection name to search in, optional. If not provided,
                                    the default collection is used.
            :param limit: The maximum number of entries to return, optional. Default is 10.
            :return: A list of found entries.
            """
            await ctx.debug(f"Finding results for query {query}")
            if collection_name:
                await ctx.debug(f"Replacing collection name with {collection_name}")

            entries = await self.qdrant_connector.search(
                query,
                collection_name=collection_name,
                limit=self.qdrant_settings.search_limit,
            )
            translator = get_translator()
            if not entries:
                return [translator.translate("tools.find.no_results", query=query)]
            content = [
                translator.translate("tools.find.results_header", query=query),
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
        translator = get_translator()

        if self.qdrant_settings.collection_name:
            self.add_tool(
                find_with_default_collection,
                name="qdrant-find",
                description=translator.translate("tools.find.description"),
            )
        else:
            self.add_tool(
                find,
                name="qdrant-find",
                description=translator.translate("tools.find.description"),
            )

        if not self.qdrant_settings.read_only:
            # Those methods can modify the database

            if self.qdrant_settings.collection_name:
                self.add_tool(
                    store_with_default_collection,
                    name="qdrant-store",
                    description=translator.translate("tools.store.description"),
                )
            else:
                self.add_tool(
                    store,
                    name="qdrant-store",
                    description=translator.translate("tools.store.description"),
                )

        # Load additional tools from plugins
        try:
            from synapstor.plugins import load_plugin_tools

            plugin_tools = load_plugin_tools(self)
            if plugin_tools:
                logger.info(f"Tools loaded from plugins: {', '.join(plugin_tools)}")
        except Exception as e:
            logger.warning(f"Error loading plugins: {e}")
