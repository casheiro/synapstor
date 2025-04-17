import uuid

import pytest

from synapstor.embeddings.fastembed import FastEmbedProvider
from synapstor.qdrant import Entry, QdrantConnector


@pytest.fixture
async def embedding_provider():
    """Fixture para fornecer um provedor de embeddings FastEmbed."""
    return FastEmbedProvider(model_name="sentence-transformers/all-MiniLM-L6-v2")


@pytest.fixture
async def qdrant_connector(embedding_provider):
    """Fixture para fornecer um QdrantConnector com cliente Qdrant em memória."""
    # Use um nome de coleção aleatório para evitar conflitos entre testes
    collection_name = f"test_collection_{uuid.uuid4().hex}"

    # Cria o conector com Qdrant em memória
    connector = QdrantConnector(
        qdrant_url=":memory:",
        qdrant_api_key=None,
        collection_name=collection_name,
        embedding_provider=embedding_provider,
    )

    yield connector


@pytest.mark.asyncio
async def test_store_and_search(qdrant_connector):
    """Testa o armazenamento de uma entrada e depois a busca por ela."""
    # Armazena uma entrada de teste
    test_entry = Entry(
        content="The quick brown fox jumps over the lazy dog",
        metadata={"source": "test", "importance": "high"},
    )
    await qdrant_connector.store(test_entry)

    # Busca pela entrada
    results = await qdrant_connector.search("fox jumps")

    # Verifica os resultados
    assert len(results) == 1
    assert results[0].content == test_entry.content
    assert results[0].metadata == test_entry.metadata


@pytest.mark.asyncio
async def test_search_empty_collection(qdrant_connector):
    """Testa a busca em uma coleção vazia."""
    # Busca em uma coleção vazia
    results = await qdrant_connector.search("test query")

    # Verifica os resultados
    assert len(results) == 0


@pytest.mark.asyncio
async def test_multiple_entries(qdrant_connector):
    """Testa o armazenamento e busca de múltiplas entradas."""
    # Armazena múltiplas entradas
    entries = [
        Entry(
            content="Python is a programming language",
            metadata={"topic": "programming"},
        ),
        Entry(content="The Eiffel Tower is in Paris", metadata={"topic": "landmarks"}),
        Entry(content="Machine learning is a subset of AI", metadata={"topic": "AI"}),
    ]

    for entry in entries:
        await qdrant_connector.store(entry)

    # Busca por entradas relacionadas a programação
    programming_results = await qdrant_connector.search("Python programming")
    assert len(programming_results) > 0
    assert any("Python" in result.content for result in programming_results)

    # Busca por entradas relacionadas a pontos turísticos
    landmark_results = await qdrant_connector.search("Eiffel Tower Paris")
    assert len(landmark_results) > 0
    assert any("Eiffel" in result.content for result in landmark_results)

    # Busca por entradas relacionadas a IA
    ai_results = await qdrant_connector.search(
        "artificial intelligence machine learning"
    )
    assert len(ai_results) > 0
    assert any("machine learning" in result.content.lower() for result in ai_results)


@pytest.mark.asyncio
async def test_ensure_collection_exists(qdrant_connector):
    """Testa se a coleção é criada caso não exista."""
    # A coleção não deve existir ainda
    assert not await qdrant_connector._client.collection_exists(
        qdrant_connector._default_collection_name
    )

    # Armazenar uma entrada deve criar a coleção
    test_entry = Entry(content="Test content")
    await qdrant_connector.store(test_entry)

    # Agora a coleção deve existir
    assert await qdrant_connector._client.collection_exists(
        qdrant_connector._default_collection_name
    )


@pytest.mark.asyncio
async def test_metadata_handling(qdrant_connector):
    """Testa se os metadados são armazenados e recuperados corretamente."""
    # Armazena entradas com diferentes metadados
    metadata1 = {"source": "book", "author": "Jane Doe", "year": 2023}
    metadata2 = {"source": "article", "tags": ["science", "research"]}

    await qdrant_connector.store(
        Entry(content="Content with structured metadata", metadata=metadata1)
    )
    await qdrant_connector.store(
        Entry(content="Content with list in metadata", metadata=metadata2)
    )

    # Busca e verifica se os metadados foram preservados
    results = await qdrant_connector.search("metadata")

    assert len(results) == 2

    # Verifica se ambos os objetos de metadados estão presentes nos resultados
    found_metadata1 = False
    found_metadata2 = False

    for result in results:
        if result.metadata.get("source") == "book":
            assert result.metadata.get("author") == "Jane Doe"
            assert result.metadata.get("year") == 2023
            found_metadata1 = True
        elif result.metadata.get("source") == "article":
            assert "science" in result.metadata.get("tags", [])
            assert "research" in result.metadata.get("tags", [])
            found_metadata2 = True

    assert found_metadata1
    assert found_metadata2


@pytest.mark.asyncio
async def test_entry_without_metadata(qdrant_connector):
    """Testa o armazenamento e recuperação de entradas sem metadados."""
    # Armazena uma entrada sem metadados
    await qdrant_connector.store(Entry(content="Entry without metadata"))

    # Busca e verifica
    results = await qdrant_connector.search("without metadata")

    assert len(results) == 1
    assert results[0].content == "Entry without metadata"
    assert results[0].metadata is None


@pytest.mark.asyncio
async def test_custom_collection_store_and_search(qdrant_connector):
    """Testa o armazenamento e busca em uma coleção personalizada."""
    # Define um nome de coleção personalizado
    custom_collection = f"custom_collection_{uuid.uuid4().hex}"

    # Armazena uma entrada de teste na coleção personalizada
    test_entry = Entry(
        content="This is stored in a custom collection",
        metadata={"custom": True},
    )
    await qdrant_connector.store(test_entry, collection_name=custom_collection)

    # Busca na coleção personalizada
    results = await qdrant_connector.search(
        "custom collection", collection_name=custom_collection
    )

    # Verifica os resultados
    assert len(results) == 1
    assert results[0].content == test_entry.content
    assert results[0].metadata == test_entry.metadata

    # Verifica se a entrada não está na coleção padrão
    default_results = await qdrant_connector.search("custom collection")
    assert len(default_results) == 0


@pytest.mark.asyncio
async def test_multiple_collections(qdrant_connector):
    """Testa o uso de múltiplas coleções com o mesmo conector."""
    # Define dois nomes de coleções personalizadas
    collection_a = f"collection_a_{uuid.uuid4().hex}"
    collection_b = f"collection_b_{uuid.uuid4().hex}"

    # Armazena entradas em diferentes coleções
    entry_a = Entry(
        content="This belongs to collection A", metadata={"collection": "A"}
    )
    entry_b = Entry(
        content="This belongs to collection B", metadata={"collection": "B"}
    )
    entry_default = Entry(content="This belongs to the default collection")

    await qdrant_connector.store(entry_a, collection_name=collection_a)
    await qdrant_connector.store(entry_b, collection_name=collection_b)
    await qdrant_connector.store(entry_default)

    # Busca na coleção A
    results_a = await qdrant_connector.search("belongs", collection_name=collection_a)
    assert len(results_a) == 1
    assert results_a[0].content == entry_a.content

    # Busca na coleção B
    results_b = await qdrant_connector.search("belongs", collection_name=collection_b)
    assert len(results_b) == 1
    assert results_b[0].content == entry_b.content

    # Busca na coleção padrão
    results_default = await qdrant_connector.search("belongs")
    assert len(results_default) == 1
    assert results_default[0].content == entry_default.content


@pytest.mark.asyncio
async def test_nonexistent_collection_search(qdrant_connector):
    """Testa a busca em uma coleção que não existe."""
    # Busca em uma coleção que não existe
    nonexistent_collection = f"nonexistent_{uuid.uuid4().hex}"
    results = await qdrant_connector.search(
        "test query", collection_name=nonexistent_collection
    )

    # Verifica os resultados
    assert len(results) == 0
