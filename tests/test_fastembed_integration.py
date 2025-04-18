import numpy as np
import pytest
from fastembed import TextEmbedding

from synapstor.embeddings.fastembed import FastEmbedProvider


@pytest.mark.asyncio
class TestFastEmbedProviderIntegration:
    """Integration tests for the FastEmbedProvider."""

    async def test_initialization(self):
        """Tests if the provider can be initialized with a valid model."""
        provider = FastEmbedProvider("sentence-transformers/all-MiniLM-L6-v2")
        assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert isinstance(provider.embedding_model, TextEmbedding)

    async def test_embed_documents(self):
        """Tests if documents can be converted into embeddings."""
        provider = FastEmbedProvider("sentence-transformers/all-MiniLM-L6-v2")
        documents = ["This is a test document.", "This is another test document."]

        embeddings = await provider.embed_documents(documents)

        # Check if we got the correct number of embeddings
        assert len(embeddings) == len(documents)

        # Check if embeddings have the expected format
        # The exact dimension depends on the model, but it should be consistent
        assert len(embeddings[0]) > 0
        assert all(len(embedding) == len(embeddings[0]) for embedding in embeddings)

        # Check if embeddings are different for different documents
        # Convert to numpy arrays for easier comparison
        embedding1 = np.array(embeddings[0])
        embedding2 = np.array(embeddings[1])
        assert not np.array_equal(embedding1, embedding2)

    async def test_embed_query(self):
        """Tests if queries can be converted into embeddings."""
        provider = FastEmbedProvider("sentence-transformers/all-MiniLM-L6-v2")
        query = "This is a test query."

        embedding = await provider.embed_query(query)

        # Check if the embedding has the expected format
        assert len(embedding) > 0

        # Convert the same query again to check consistency
        embedding2 = await provider.embed_query(query)
        assert len(embedding) == len(embedding2)

        # Embeddings should be identical for the same input
        np.testing.assert_array_almost_equal(np.array(embedding), np.array(embedding2))

    async def test_get_vector_name(self):
        """Tests if the vector name is generated correctly."""
        provider = FastEmbedProvider("sentence-transformers/all-MiniLM-L6-v2")
        vector_name = provider.get_vector_name()

        # Check if the vector name follows the expected format
        assert vector_name.startswith("fast-")
        assert "minilm" in vector_name.lower()
