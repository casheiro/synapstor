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

        # Configure language
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
        Format entry with MEF-aware presentation when available.
        """
        if not entry.metadata:
            return f"<entry><content>{entry.content}</content></entry>"

        # Check if this is a MEF document
        is_mef = entry.metadata.get("is_mef_document", False)

        if is_mef:
            return self._format_mef_entry(entry)
        else:
            return self._format_standard_entry(entry)

    def _format_mef_entry(self, entry: Entry) -> str:
        """Format MEF document entry with structured presentation."""
        metadata = entry.metadata

        # Build MEF-specific header
        mef_info = []
        if metadata.get("mef_id"):
            mef_info.append(f"ID: {metadata['mef_id']}")
        if metadata.get("mef_domain"):
            mef_info.append(f"Domain: {metadata['mef_domain']}")
        if metadata.get("mef_type"):
            mef_info.append(f"Type: {metadata['mef_type']}")
        if metadata.get("mef_context"):
            mef_info.append(f"Context: {metadata['mef_context']}")

        mef_header = f"[MEF: {' | '.join(mef_info)}]" if mef_info else "[MEF Document]"

        # Add usage information if available
        usage_info = []
        if metadata.get("mef_intent_of_use"):
            usage_info.append(f"Intent: {', '.join(metadata['mef_intent_of_use'])}")
        if metadata.get("mef_use_case_stage"):
            usage_info.append(f"Stages: {', '.join(metadata['mef_use_case_stage'])}")

        usage_section = ""
        if usage_info:
            usage_section = f"<usage>{' | '.join(usage_info)}</usage>"

        # Add related UKIs if available
        related_section = ""
        if metadata.get("mef_related_to"):
            related_ukis = ", ".join(metadata["mef_related_to"])
            related_section = f"<related_ukis>{related_ukis}</related_ukis>"

        # File information
        file_path = metadata.get("caminho_relativo", metadata.get("nome_arquivo", ""))
        file_info = f"<file>{file_path}</file>" if file_path else ""

        # Combine all parts
        parts = [
            f"<mef_header>{mef_header}</mef_header>",
            file_info,
            usage_section,
            related_section,
            f"<content>{entry.content}</content>",
        ]

        return f"<entry>{''.join(part for part in parts if part)}</entry>"

    def _format_standard_entry(self, entry: Entry) -> str:
        """Format standard (non-MEF) entry."""
        # Include basic file information if available
        file_info = ""
        if entry.metadata:
            file_path = entry.metadata.get(
                "caminho_relativo", entry.metadata.get("nome_arquivo", "")
            )
            if file_path:
                file_info = f"<file>{file_path}</file>"

            # Add project information if available
            if entry.metadata.get("projeto"):
                project_info = f"<project>{entry.metadata['projeto']}</project>"
                file_info = project_info + file_info

        entry_metadata = json.dumps(entry.metadata) if entry.metadata else ""
        metadata_section = (
            f"<metadata>{entry_metadata}</metadata>" if entry_metadata else ""
        )

        return f"<entry>{file_info}<content>{entry.content}</content>{metadata_section}</entry>"

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
                return translator.translate(
                    "tools.store.success_with_collection",
                    information=information,
                    collection_name=collection_name,
                )
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
