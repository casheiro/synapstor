import uuid
import pytest
import pytest_asyncio

from synapstor.qdrant import QdrantConnector
from synapstor.embeddings.fastembed import FastEmbedProvider


def pytest_configure(config):
    """Global configuration for tests."""
    # Configuration to fix asyncio warnings
    config.option.asyncio_mode = "auto"
    pytest.asyncio_default_fixture_loop_scope = "function"


@pytest_asyncio.fixture
async def embedding_provider():
    """Fixture for the embedding provider."""
    return FastEmbedProvider(embedding_model="sentence-transformers/all-MiniLM-L6-v2")


@pytest_asyncio.fixture
async def qdrant_connector(embedding_provider):
    """Fixture for the Qdrant connector.

    This fixture creates a temporary test collection and removes it after the test.
    """
    # Generate a unique collection name for tests
    collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"

    # Configure Qdrant with the test collection
    # We no longer use the configuration object, but pass parameters directly
    connector = QdrantConnector(
        qdrant_url="http://localhost:6333",
        qdrant_api_key=None,
        collection_name=collection_name,
        embedding_provider=embedding_provider,
    )

    # Check if the collection exists and create it if necessary
    await connector._ensure_collection_exists(connector._default_collection_name)

    # Return the connector for use in tests
    try:
        yield connector
    finally:
        # Clean up after tests
        try:
            if connector._default_collection_name:
                await connector._client.delete_collection(
                    connector._default_collection_name
                )
        except Exception:
            # Ignore errors during cleanup
            pass
