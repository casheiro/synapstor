import numpy as np
import pytest
from fastembed import TextEmbedding

from synapstor.embeddings.fastembed import FastEmbedProvider


@pytest.mark.asyncio
class TestFastEmbedProviderIntegration:
    """Testes de integração para o FastEmbedProvider."""

    async def test_initialization(self):
        """Testa se o provedor pode ser inicializado com um modelo válido."""
        provider = FastEmbedProvider("sentence-transformers/all-MiniLM-L6-v2")
        assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert isinstance(provider.embedding_model, TextEmbedding)

    async def test_embed_documents(self):
        """Testa se os documentos podem ser convertidos em embeddings."""
        provider = FastEmbedProvider("sentence-transformers/all-MiniLM-L6-v2")
        documents = ["This is a test document.", "This is another test document."]

        embeddings = await provider.embed_documents(documents)

        # Verifica se obtivemos o número correto de embeddings
        assert len(embeddings) == len(documents)

        # Verifica se os embeddings têm o formato esperado
        # A dimensão exata depende do modelo, mas deve ser consistente
        assert len(embeddings[0]) > 0
        assert all(len(embedding) == len(embeddings[0]) for embedding in embeddings)

        # Verifica se os embeddings são diferentes para documentos diferentes
        # Converte para arrays numpy para facilitar a comparação
        embedding1 = np.array(embeddings[0])
        embedding2 = np.array(embeddings[1])
        assert not np.array_equal(embedding1, embedding2)

    async def test_embed_query(self):
        """Testa se as consultas podem ser convertidas em embeddings."""
        provider = FastEmbedProvider("sentence-transformers/all-MiniLM-L6-v2")
        query = "This is a test query."

        embedding = await provider.embed_query(query)

        # Verifica se o embedding tem o formato esperado
        assert len(embedding) > 0

        # Converte a mesma consulta novamente para verificar a consistência
        embedding2 = await provider.embed_query(query)
        assert len(embedding) == len(embedding2)

        # Os embeddings devem ser idênticos para a mesma entrada
        np.testing.assert_array_almost_equal(np.array(embedding), np.array(embedding2))

    async def test_get_vector_name(self):
        """Testa se o nome do vetor é gerado corretamente."""
        provider = FastEmbedProvider("sentence-transformers/all-MiniLM-L6-v2")
        vector_name = provider.get_vector_name()

        # Verifica se o nome do vetor segue o formato esperado
        assert vector_name.startswith("fast-")
        assert "minilm" in vector_name.lower()
