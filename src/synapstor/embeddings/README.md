# Módulo de Embeddings do Synapstor

Este módulo fornece uma interface unificada para geração de embeddings de texto, que são usados para armazenar e recuperar informações no Qdrant.

## Visão Geral

O sistema foi projetado usando o padrão de design **Factory** e **Strategy**, permitindo fácil extensão para suportar diferentes provedores de embeddings. Atualmente, o Synapstor suporta:

- **FastEmbed** - Uma biblioteca eficiente para geração de embeddings, usando modelos do HuggingFace

## Arquitetura

O módulo é composto por:

### Tipos (`types.py`)

Define os tipos de provedores de embeddings suportados:
```python
class EmbeddingProviderType(Enum):
    FASTEMBED = "fastembed"
    # Outros provedores podem ser adicionados no futuro
```

### Interface Base (`base.py`)

Define a interface que todos os provedores de embeddings devem implementar:

```python
class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Converte documentos em vetores de embeddings."""
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """Converte uma consulta em vetor de embedding."""
        pass

    @abstractmethod
    def get_vector_name(self) -> str:
        """Retorna o nome do vetor para a coleção Qdrant."""
        pass

    @abstractmethod
    def get_vector_size(self) -> int:
        """Retorna o tamanho do vetor para a coleção Qdrant."""
        pass
```

### Implementação FastEmbed (`fastembed.py`)

Implementa a interface `EmbeddingProvider` usando a biblioteca FastEmbed:

```python
class FastEmbedProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embedding_model = TextEmbedding(model_name)

    # Implementações dos métodos da interface
```

### Factory (`factory.py`)

Cria a instância apropriada do provedor de embeddings com base nas configurações:

```python
def create_embedding_provider(settings: EmbeddingProviderSettings) -> EmbeddingProvider:
    if settings.provider_type == EmbeddingProviderType.FASTEMBED:
        return FastEmbedProvider(settings.model_name)
    else:
        raise ValueError(f"Provedor de embeddings não suportado: {settings.provider_type}")
```

## Configuração

A configuração dos embeddings é feita através das variáveis de ambiente, que são carregadas usando o padrão Pydantic:

```python
class EmbeddingProviderSettings(BaseSettings):
    provider_type: EmbeddingProviderType = Field(
        default=EmbeddingProviderType.FASTEMBED,
        validation_alias="EMBEDDING_PROVIDER"
    )
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL"
    )
```

### Variáveis de Ambiente

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `EMBEDDING_PROVIDER` | Provedor de embeddings | `fastembed` |
| `EMBEDDING_MODEL` | Modelo usado pelo provedor | `sentence-transformers/all-MiniLM-L6-v2` |

## Uso

### Inicialização

```python
from synapstor.settings import EmbeddingProviderSettings
from synapstor.embeddings.factory import create_embedding_provider

# Carrega configurações do arquivo .env
settings = EmbeddingProviderSettings()

# Cria o provedor de embeddings
embedding_provider = create_embedding_provider(settings)
```

### Geração de Embeddings

```python
# Para documentos
documents = ["Este é um exemplo de documento", "Este é outro documento"]
embeddings = await embedding_provider.embed_documents(documents)

# Para consultas
query = "Exemplo de consulta"
query_embedding = await embedding_provider.embed_query(query)
```

### Metadados para Qdrant

```python
# Obtém o nome do vetor para configuração da coleção Qdrant
vector_name = embedding_provider.get_vector_name()

# Obtém o tamanho do vetor
vector_size = embedding_provider.get_vector_size()
```

## Extensibilidade

Para adicionar um novo provedor de embeddings:

1. Adicione um novo tipo em `EmbeddingProviderType`
2. Crie uma nova classe que implemente a interface `EmbeddingProvider`
3. Atualize a factory em `create_embedding_provider`

Exemplo:

```python
# Em types.py
class EmbeddingProviderType(Enum):
    FASTEMBED = "fastembed"
    OPENAI = "openai"  # Novo provedor

# Nova implementação em openai.py
class OpenAIProvider(EmbeddingProvider):
    # Implementação dos métodos

# Atualização da factory
def create_embedding_provider(settings: EmbeddingProviderSettings) -> EmbeddingProvider:
    if settings.provider_type == EmbeddingProviderType.FASTEMBED:
        return FastEmbedProvider(settings.model_name)
    elif settings.provider_type == EmbeddingProviderType.OPENAI:
        return OpenAIProvider(settings.model_name)
    else:
        raise ValueError(f"Provedor de embeddings não suportado: {settings.provider_type}")
```

## Dependências

- `fastembed`: Biblioteca para geração eficiente de embeddings
- `pydantic`: Para gerenciamento de configurações
- `asyncio`: Para operações assíncronas
