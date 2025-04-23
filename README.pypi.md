# Synapstor 📚🔍

**Python 3.10+ | MIT License**

## 🌎 Idioma / Language

- [Português 🇧🇷](#português)
- [English 🇺🇸](#english)

---

<a name="português"></a>
# Português 🇧🇷

> **Synapstor** é uma biblioteca modular para armazenamento e recuperação semântica de informações usando embeddings vetoriais e banco de dados Qdrant.
>
> **Nota**: O Synapstor é uma evolução não oficial do projeto mcp-server-qdrant, expandindo suas funcionalidades para criar uma solução mais abrangente para armazenamento e recuperação semântica.

## 🔭 Visão Geral

Synapstor é uma solução completa para armazenamento e recuperação de informações baseada em embeddings vetoriais. Combinando a potência do Qdrant (banco de dados vetorial) com modelos modernos de embeddings, o Synapstor permite:

- 🔍 **Busca semântica** em documentos, código e outros conteúdos textuais
- 🧠 **Armazenamento eficiente** de informações com metadados associados
- 🔄 **Integração com LLMs** através do Protocolo MCP (Model Control Protocol)
- 🛠️ **Ferramentas CLI** para indexação e consulta de dados

## 🖥️ Requisitos

- **Python**: 3.10 ou superior
- **Qdrant**: Banco de dados vetorial para armazenamento e busca de embeddings
- **Modelos de Embedding**: Por padrão, usa modelos da biblioteca FastEmbed

## 📦 Instalação

```bash
# Instalação básica via pip
pip install synapstor

# Com suporte a embeddings rápidos (recomendado)
pip install "synapstor[fastembed]"

# Para desenvolvimento (formatadores, linters)
pip install "synapstor[dev]"

# Para testes
pip install "synapstor[test]"

# Instalação completa (todos os recursos e ferramentas)
pip install "synapstor[all]"
```

## 🚀 Uso Rápido

### Configuração

Existem várias formas de configurar o Synapstor:

1. **Variáveis de ambiente**:
   ```bash
   # Exportar as variáveis no shell (Linux/macOS)
   export QDRANT_URL="http://localhost:6333"
   export QDRANT_API_KEY="sua-chave-api"
   export COLLECTION_NAME="synapstor"
   export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

   # Ou no Windows (PowerShell)
   $env:QDRANT_URL = "http://localhost:6333"
   $env:QDRANT_API_KEY = "sua-chave-api"
   $env:COLLECTION_NAME = "synapstor"
   $env:EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
   ```

2. **Parâmetros na linha de comando**:
   ```bash
   synapstor-ctl start --qdrant-url http://localhost:6333 --qdrant-api-key sua-chave-api --collection-name synapstor --embedding-model "sentence-transformers/all-MiniLM-L6-v2"
   ```

3. **Programaticamente** (para uso como biblioteca):
   ```python
   from synapstor.settings import Settings

   settings = Settings(
       qdrant_url="http://localhost:6333",
       qdrant_api_key="sua-chave-api",
       collection_name="minha_colecao",
       embedding_model="sentence-transformers/all-MiniLM-L6-v2"
   )
   ```

### Como servidor MCP

```bash
# Iniciar o servidor MCP com a interface centralizada
synapstor-ctl start

# Com parâmetros de configuração
synapstor-ctl start --qdrant-url http://localhost:6333 --qdrant-api-key sua-chave-api --collection-name minha_colecao --embedding-model "sentence-transformers/all-MiniLM-L6-v2"
```

### Indexação de projetos

```bash
# Indexar um projeto
synapstor-ctl indexer --project meu-projeto --path /caminho/do/projeto
```

### Como biblioteca em aplicações Python

```python
from synapstor.qdrant import QdrantConnector, Entry
from synapstor.embeddings.factory import create_embedding_provider
from synapstor.settings import EmbeddingProviderSettings

# Inicializar componentes
settings = EmbeddingProviderSettings()
embedding_provider = create_embedding_provider(settings)

connector = QdrantConnector(
    qdrant_url="http://localhost:6333",
    collection_name="minha_colecao",
    embedding_provider=embedding_provider
)

# Armazenar informações
async def store_data():
    entry = Entry(
        content="Conteúdo a ser armazenado",
        metadata={"chave": "valor"}
    )
    await connector.store(entry)

# Buscar informações
async def search_data():
    results = await connector.search("consulta em linguagem natural")
    for result in results:
        print(result.content)
```

## 📚 Documentação Completa

Para documentação detalhada, exemplos avançados, integração com diferentes LLMs, deployment com Docker, e outras informações, visite o [repositório no GitHub](https://github.com/casheiro/synapstor).

---

<a name="english"></a>
# English 🇺🇸

> **Synapstor** is a modular library for semantic storage and retrieval of information using vector embeddings and the Qdrant database.
>
> **Note**: Synapstor is an unofficial evolution of the mcp-server-qdrant project, expanding its functionality to create a more comprehensive solution for semantic storage and retrieval.

## 🔭 Overview

Synapstor is a complete solution for storing and retrieving information based on vector embeddings. Combining the power of Qdrant (vector database) with modern embedding models, Synapstor allows:

- 🔍 **Semantic search** in documents, code, and other textual content
- 🧠 **Efficient storage** of information with associated metadata
- 🔄 **Integration with LLMs** through the MCP (Model Control Protocol)
- 🛠️ **CLI tools** for indexing and querying data

## 🖥️ Requirements

- **Python**: 3.10 or higher
- **Qdrant**: Vector database for storing and searching embeddings
- **Embedding Models**: By default, uses models from the FastEmbed library

## 📦 Installation

```bash
# Basic installation via pip
pip install synapstor

# With fast embedding support (recommended)
pip install "synapstor[fastembed]"

# For development (formatters, linters)
pip install "synapstor[dev]"

# For testing
pip install "synapstor[test]"

# Complete installation (all features and tools)
pip install "synapstor[all]"
```

## 🚀 Quick Usage

### Configuration

There are several ways to configure Synapstor:

1. **Environment variables**:
   ```bash
   # Export variables in shell (Linux/macOS)
   export QDRANT_URL="http://localhost:6333"
   export QDRANT_API_KEY="your-api-key"
   export COLLECTION_NAME="synapstor"
   export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

   # Or on Windows (PowerShell)
   $env:QDRANT_URL = "http://localhost:6333"
   $env:QDRANT_API_KEY = "your-api-key"
   $env:COLLECTION_NAME = "synapstor"
   $env:EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
   ```

2. **Command line parameters**:
   ```bash
   synapstor-ctl start --qdrant-url http://localhost:6333 --qdrant-api-key your-api-key --collection-name synapstor --embedding-model "sentence-transformers/all-MiniLM-L6-v2"
   ```

3. **Programmatically** (for use as a library):
   ```python
   from synapstor.settings import Settings

   settings = Settings(
       qdrant_url="http://localhost:6333",
       qdrant_api_key="your-api-key",
       collection_name="my_collection",
       embedding_model="sentence-transformers/all-MiniLM-L6-v2"
   )
   ```

### As an MCP server

```bash
# Start the MCP server with the centralized interface
synapstor-ctl start

# With configuration parameters
synapstor-ctl start --qdrant-url http://localhost:6333 --qdrant-api-key your-api-key --collection-name my_collection --embedding-model "sentence-transformers/all-MiniLM-L6-v2"
```

### Project indexing

```bash
# Index a project
synapstor-ctl indexer --project my-project --path /path/to/project
```

### As a library in Python applications

```python
from synapstor.qdrant import QdrantConnector, Entry
from synapstor.embeddings.factory import create_embedding_provider
from synapstor.settings import EmbeddingProviderSettings

# Initialize components
settings = EmbeddingProviderSettings()
embedding_provider = create_embedding_provider(settings)

connector = QdrantConnector(
    qdrant_url="http://localhost:6333",
    collection_name="my_collection",
    embedding_provider=embedding_provider
)

# Store information
async def store_data():
    entry = Entry(
        content="Content to be stored",
        metadata={"key": "value"}
    )
    await connector.store(entry)

# Search for information
async def search_data():
    results = await connector.search("natural language query")
    for result in results:
        print(result.content)
```

## 📚 Complete Documentation

For detailed documentation, advanced examples, integration with different LLMs, Docker deployment, and other information, visit the [GitHub repository](https://github.com/casheiro/synapstor).

---

Developed with ❤️ by the Synapstor team
