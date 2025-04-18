# Módulo de Embeddings

## 🌎 Idioma / Language

- [Português 🇧🇷](#português)
- [English 🇺🇸](#english)

---

<a name="português"></a>
# Português 🇧🇷

O módulo de embeddings do Synapstor fornece funcionalidades para converter texto em representações vetoriais (embeddings) que capturam o significado semântico do conteúdo. Estas representações são essenciais para realizar pesquisas semânticas eficientes.

## Características Principais

- **Múltiplos modelos suportados**: Integração com modelos populares de embeddings como os da OpenAI, Sentence Transformers e outros
- **Adaptadores flexíveis**: Arquitetura que permite adicionar facilmente novos modelos de embeddings
- **Geração em lote**: Processamento eficiente de múltiplos textos em uma única requisição
- **Caching inteligente**: Redução de custos e latência através de caching de embeddings anteriores
- **Detecção automática**: Seleção inteligente do modelo mais adequado com base no conteúdo

## Arquitetura

O módulo é organizado com os seguintes componentes:

### `embeddings_factory.py`

Implementa o padrão Factory para criação de instâncias de geradores de embeddings, permitindo selecionar dinamicamente o modelo mais adequado para cada caso de uso.

```python
from synapstor.embeddings import get_embeddings_generator

# Obter um gerador de embeddings usando o modelo padrão
generator = get_embeddings_generator()

# Ou especificar um modelo particular
generator = get_embeddings_generator(model_name="sentence-transformers/all-MiniLM-L6-v2")
```

### `base_generator.py`

Define a interface comum (`BaseEmbeddingsGenerator`) que todos os geradores de embeddings devem implementar, garantindo consistência entre diferentes implementações.

### Adaptadores de Modelo

- `openai_generator.py`: Integrações com modelos da OpenAI
- `st_generator.py`: Integrações com modelos Sentence Transformers
- `huggingface_generator.py`: Integrações com modelos do Hugging Face

## Exemplo de Uso

```python
from synapstor.embeddings import get_embeddings_generator

# Inicializar o gerador de embeddings
embedding_generator = get_embeddings_generator(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_dir="./cache"
)

# Gerar embeddings para um único texto
texto = "O Synapstor é uma ferramenta para armazenamento e pesquisa semântica de código"
embedding = embedding_generator.get_embeddings(texto)

# Gerar embeddings para múltiplos textos
textos = [
    "Pesquisa semântica de código",
    "Armazenamento de conhecimento",
    "Assistente de programação"
]
embeddings = embedding_generator.get_batch_embeddings(textos)

# Verificar a dimensionalidade
print(f"Dimensão do embedding: {len(embedding)}")
```

## Configuração Avançada

### Cache de Embeddings

Para evitar recalcular embeddings já gerados anteriormente:

```python
from synapstor.embeddings import get_embeddings_generator

# Ativar cache para economizar recursos
generator = get_embeddings_generator(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    use_cache=True,
    cache_dir="./embeddings_cache"
)

# Os embeddings serão armazenados localmente
# e reutilizados em chamadas futuras com os mesmos textos
```

### Normalização de Embeddings

Normalização para garantir consistência nas operações de similaridade:

```python
from synapstor.embeddings import get_embeddings_generator

# Ativar normalização automática (L2)
generator = get_embeddings_generator(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    normalize=True
)

# Todos os embeddings gerados terão norma = 1
```

## Seleção de Modelo

Recomendações de modelos para diferentes casos de uso:

- **Uso geral**: `sentence-transformers/all-MiniLM-L6-v2` (padrão)
- **Português**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Precisão máxima**: `sentence-transformers/all-mpnet-base-v2`
- **Velocidade máxima**: `sentence-transformers/all-MiniLM-L3-v2`

## Desempenho e Otimização

Técnicas para otimizar o uso de recursos:

- Use `get_batch_embeddings()` para processar múltiplos textos de uma vez
- Ative o cache para textos frequentes ou para economizar chamadas de API
- Selecione modelos menores quando a velocidade for mais importante que a precisão
- Execute localmente modelos Sentence Transformers para evitar custos de API

---

<a name="english"></a>
# English 🇺🇸

The Synapstor embeddings module provides functionality to convert text into vector representations (embeddings) that capture the semantic meaning of content. These representations are essential for performing efficient semantic searches.

## Main Features

- **Multiple supported models**: Integration with popular embedding models such as OpenAI, Sentence Transformers, and others
- **Flexible adapters**: Architecture that allows easy addition of new embedding models
- **Batch generation**: Efficient processing of multiple texts in a single request
- **Intelligent caching**: Reduction of costs and latency through caching of previous embeddings
- **Automatic detection**: Intelligent selection of the most suitable model based on content

## Architecture

The module is organized with the following components:

### `embeddings_factory.py`

Implements the Factory pattern for creating instances of embedding generators, allowing dynamic selection of the most suitable model for each use case.

```python
from synapstor.embeddings import get_embeddings_generator

# Get an embeddings generator using the default model
generator = get_embeddings_generator()

# Or specify a particular model
generator = get_embeddings_generator(model_name="sentence-transformers/all-MiniLM-L6-v2")
```

### `base_generator.py`

Defines the common interface (`BaseEmbeddingsGenerator`) that all embedding generators must implement, ensuring consistency across different implementations.

### Model Adapters

- `openai_generator.py`: Integrations with OpenAI models
- `st_generator.py`: Integrations with Sentence Transformers models
- `huggingface_generator.py`: Integrations with Hugging Face models

## Usage Example

```python
from synapstor.embeddings import get_embeddings_generator

# Initialize the embeddings generator
embedding_generator = get_embeddings_generator(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_dir="./cache"
)

# Generate embeddings for a single text
text = "Synapstor is a tool for storing and semantically searching code"
embedding = embedding_generator.get_embeddings(text)

# Generate embeddings for multiple texts
texts = [
    "Semantic code search",
    "Knowledge storage",
    "Programming assistant"
]
embeddings = embedding_generator.get_batch_embeddings(texts)

# Check dimensionality
print(f"Embedding dimension: {len(embedding)}")
```

## Advanced Configuration

### Embeddings Cache

To avoid recalculating previously generated embeddings:

```python
from synapstor.embeddings import get_embeddings_generator

# Enable caching to save resources
generator = get_embeddings_generator(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    use_cache=True,
    cache_dir="./embeddings_cache"
)

# Embeddings will be stored locally
# and reused in future calls with the same texts
```

### Embeddings Normalization

Normalization to ensure consistency in similarity operations:

```python
from synapstor.embeddings import get_embeddings_generator

# Enable automatic normalization (L2)
generator = get_embeddings_generator(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    normalize=True
)

# All generated embeddings will have norm = 1
```

## Model Selection

Recommended models for different use cases:

- **General use**: `sentence-transformers/all-MiniLM-L6-v2` (default)
- **Portuguese**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Maximum accuracy**: `sentence-transformers/all-mpnet-base-v2`
- **Maximum speed**: `sentence-transformers/all-MiniLM-L3-v2`

## Performance and Optimization

Techniques to optimize resource usage:

- Use `get_batch_embeddings()` to process multiple texts at once
- Enable caching for frequent texts or to save API calls
- Select smaller models when speed is more important than accuracy
- Run Sentence Transformers models locally to avoid API costs
