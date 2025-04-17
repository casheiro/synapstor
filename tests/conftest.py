import uuid
import pytest
import pytest_asyncio

from synapstor.qdrant import QdrantConnector
from synapstor.embeddings.fastembed import FastEmbedProvider


def pytest_configure(config):
    """Configuração global para os testes."""
    # Configuração para corrigir os avisos de asyncio
    config.option.asyncio_mode = "auto"
    pytest.asyncio_default_fixture_loop_scope = "function"


@pytest_asyncio.fixture
async def embedding_provider():
    """Fixture para o provedor de embeddings."""
    return FastEmbedProvider(embedding_model="sentence-transformers/all-MiniLM-L6-v2")


@pytest_asyncio.fixture
async def qdrant_connector(embedding_provider):
    """Fixture para o conector Qdrant.
    
    Esta fixture cria uma coleção de teste temporária e a remove após o teste.
    """
    # Gerar um nome de coleção único para os testes
    collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"
    
    # Configurar o Qdrant com a coleção de teste
    # Não vamos mais usar o objeto de configurações, mas sim passando os parâmetros diretamente
    connector = QdrantConnector(
        qdrant_url="http://localhost:6333",
        qdrant_api_key=None,
        collection_name=collection_name,
        embedding_provider=embedding_provider,
    )
    
    # Verificar se a coleção existe e criá-la se necessário
    await connector._ensure_collection_exists(connector._default_collection_name)
    
    # Retornar o conector para uso nos testes
    try:
        yield connector
    finally:
        # Limpar após os testes
        try:
            if connector._default_collection_name:
                await connector._client.delete_collection(connector._default_collection_name)
        except Exception:
            # Ignorar erros na limpeza
            pass 