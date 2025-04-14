import json
import logging
import asyncio
import inspect
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar, Union, get_type_hints

# Define um tipo genérico para retornos de função
T = TypeVar("T")

logger = logging.getLogger(__name__)

# Implementação simplificada do Context e FastMCP para o Synapstor
class Context:
    """
    Contexto para as requisições do servidor.
    Permite registrar mensagens de debug e outras informações.
    """
    def __init__(self, request_id: str = None):
        self.request_id = request_id
        
    async def debug(self, message: str) -> None:
        """Registra uma mensagem de debug."""
        logger.debug(f"{self.request_id}: {message}")

class FastMCP:
    """
    Implementação simplificada do FastMCP para o Synapstor.
    Baseado no conceito original do mcp-server-qdrant.
    """
    def __init__(self, name: str = "synapstor"):
        self.name = name
        self.tools: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Inicializando servidor FastMCP '{name}'")
    
    def add_tool(
        self,
        func: Callable[..., Awaitable[T]],
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Adiciona uma ferramenta ao servidor."""
        # Se o nome não for fornecido, usa o nome da função
        if name is None:
            name = func.__name__
            
        # Se a descrição não for fornecida, usa a docstring da função
        if description is None and func.__doc__:
            description = func.__doc__.strip()
        elif description is None:
            description = f"Ferramenta {name}"
        
        # Registra a ferramenta
        self.tools[name] = {
            "func": func,
            "description": description,
        }
        
        logger.info(f"Ferramenta '{name}' registrada: {description}")
    
    def run(self, transport: str = "stdio") -> None:
        """Executa o servidor com o transporte especificado."""
        if transport == "stdio":
            logger.info("Iniciando servidor com transporte stdio")
            asyncio.run(self._run_stdio())
        elif transport == "sse":
            logger.info("Iniciando servidor com transporte SSE")
            self._run_sse()
        else:
            raise ValueError(f"Transporte '{transport}' não suportado")
    
    async def _run_stdio(self) -> None:
        """Loop básico para o transporte stdio."""
        logger.info("Servidor pronto para receber comandos via stdio")
        while True:
            try:
                print("Aguardando comando...")
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                print(f"Recebido: {line}")
            except KeyboardInterrupt:
                logger.info("Servidor interrompido")
                break
    
    def _run_sse(self) -> None:
        """Implementação básica para o transporte SSE."""
        try:
            import uvicorn
            from fastapi import FastAPI
            
            app = FastAPI()
            
            # Configuração básica da API
            @app.get("/")
            def read_root():
                return {"status": "online", "server": self.name}
            
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except ImportError:
            logger.error("Dependências para SSE não encontradas: fastapi, uvicorn")
            raise

from synapstor.embeddings.factory import create_embedding_provider
from synapstor.qdrant import Entry, Metadata, QdrantConnector
from synapstor.settings import (
    EmbeddingProviderSettings,
    QdrantSettings,
    ToolSettings,
)

# FastMCP is an alternative interface for declaring the capabilities
# of the server. Its API is based on FastAPI.
class QdrantMCPServer(FastMCP):
    """
    A MCP server for Qdrant.
    """

    def __init__(
        self,
        tool_settings: ToolSettings,
        qdrant_settings: QdrantSettings,
        embedding_provider_settings: EmbeddingProviderSettings,
        name: str = "synapstor",
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

        super().__init__(name=name)

        self.setup_tools()

    def format_entry(self, entry: Entry) -> str:
        """
        Feel free to override this method in your subclass to customize the format of the entry.
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
            :param collection_name: The name of the collection to store the information in, optional. If not provided,
                                    the default collection is used.
            :return: A message indicating that the information was stored.
            """
            await ctx.debug(f"Storing information {information} in Qdrant")

            entry = Entry(content=information, metadata=metadata)

            await self.qdrant_connector.store(entry, collection_name=collection_name)
            if collection_name:
                return f"Remembered: {information} in collection {collection_name}"
            return f"Remembered: {information}"

        async def store_with_default_collection(
            ctx: Context,
            information: str,
            metadata: Metadata = None,
        ) -> str:
            return await store(
                ctx, information, metadata, self.qdrant_settings.collection_name
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
            :param collection_name: The name of the collection to search in, optional. If not provided,
                                    the default collection is used.
            :param limit: The maximum number of entries to return, optional. Default is 10.
            :return: A list of entries found.
            """
            await ctx.debug(f"Finding results for query {query}")
            if collection_name:
                await ctx.debug(
                    f"Overriding the collection name with {collection_name}"
                )

            entries = await self.qdrant_connector.search(
                query,
                collection_name=collection_name,
                limit=self.qdrant_settings.search_limit,
            )
            if not entries:
                return [f"No information found for the query '{query}'"]
            content = [
                f"Results for the query '{query}'",
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
