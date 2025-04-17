# Testes do Synapstor

Este diretório contém os testes automatizados para validar o funcionamento adequado dos diferentes componentes do Synapstor.

## Estrutura de Testes

O diretório `tests/` está organizado da seguinte forma:

- `test_qdrant_integration.py`: Testes de integração com o banco de dados vetorial Qdrant
- `test_settings.py`: Testes para as classes de configurações do sistema
- `test_fastembed_integration.py`: Testes para o provedor de embeddings FastEmbed
- `__init__.py`: Arquivo que marca o diretório como um pacote Python

## Testes de Integração com Qdrant

O arquivo `test_qdrant_integration.py` contém testes que verificam a funcionalidade do `QdrantConnector`, responsável por armazenar e recuperar dados usando similaridade semântica.

### Funcionalidades testadas

- Armazenamento e recuperação de entradas via busca semântica
- Gerenciamento de múltiplas coleções
- Manipulação de metadados complexos
- Comportamento em casos limites (coleções vazias, inexistentes)
- Criação automática de coleções

### Exemplo de uso

```python
# Fixture para criar um conector Qdrant em memória para testes
@pytest.fixture
async def qdrant_connector(embedding_provider):
    collection_name = f"test_collection_{uuid.uuid4().hex}"
    connector = QdrantConnector(
        qdrant_url=":memory:",
        qdrant_api_key=None,
        collection_name=collection_name,
        embedding_provider=embedding_provider,
    )
    yield connector

# Teste para armazenar e buscar uma entrada
@pytest.mark.asyncio
async def test_store_and_search(qdrant_connector):
    test_entry = Entry(
        content="The quick brown fox jumps over the lazy dog",
        metadata={"source": "test", "importance": "high"},
    )
    await qdrant_connector.store(test_entry)

    results = await qdrant_connector.search("fox jumps")

    assert len(results) == 1
    assert results[0].content == test_entry.content
```

## Testes de Configurações

O arquivo `test_settings.py` testa as classes de configuração do sistema, garantindo que os parâmetros são carregados corretamente de variáveis de ambiente e valores padrão.

### Classes testadas

- `QdrantSettings`: Configurações para conexão com o banco Qdrant
- `EmbeddingProviderSettings`: Configurações para o provedor de embeddings
- `ToolSettings`: Configurações para as ferramentas do Synapstor

### Exemplo de teste

```python
@patch.dict(
    os.environ,
    {"QDRANT_URL": "http://localhost:6333", "COLLECTION_NAME": "test_collection"},
)
def test_minimal_config(self):
    """Test loading minimal configuration from environment variables."""
    settings = QdrantSettings()
    assert settings.location == "http://localhost:6333"
    assert settings.collection_name == "test_collection"
    assert settings.api_key is None
```

## Testes do FastEmbed

O arquivo `test_fastembed_integration.py` testa o provedor de embeddings FastEmbed, verificando sua inicialização e capacidade de gerar vetores de embeddings para documentos e consultas.

### Principais funcionalidades testadas

- Inicialização com diferentes modelos
- Geração de embeddings para documentos (textos)
- Geração de embeddings para consultas (queries)
- Formato e consistência dos vetores gerados

### Exemplo de teste

```python
async def test_embed_documents(self):
    """Test that documents can be embedded."""
    provider = FastEmbedProvider("sentence-transformers/all-MiniLM-L6-v2")
    documents = ["This is a test document.", "This is another test document."]

    embeddings = await provider.embed_documents(documents)

    # Check that we got the right number of embeddings
    assert len(embeddings) == len(documents)
    # Check that embeddings are different for different documents
    embedding1 = np.array(embeddings[0])
    embedding2 = np.array(embeddings[1])
    assert not np.array_equal(embedding1, embedding2)
```

## Executando os Testes

Para executar os testes, use o pytest:

```bash
# Executar todos os testes
pytest tests/

# Executar um arquivo específico de testes
pytest tests/test_qdrant_integration.py

# Executar um teste específico
pytest tests/test_qdrant_integration.py::test_store_and_search
```

Os testes são configurados para funcionar com código assíncrono através do marcador `pytest.mark.asyncio`.
