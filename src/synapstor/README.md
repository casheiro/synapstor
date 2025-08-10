# Synapstor

![Synapstor](https://2.gravatar.com/userimage/264864229/4e133a67b7d5fff345dd8f2bc4d0743b?size=400)

## 🌎 Idioma / Language

- [Português 🇧🇷](#português)
- [English 🇺🇸](#english)

---

<a name="português"></a>
# Português 🇧🇷

> Biblioteca modular para armazenamento e recuperação semântica de informações usando embeddings vetoriais.

## 🔍 Visão Geral

O Synapstor é um sistema modular para armazenamento e recuperação de informações baseado em embeddings vetoriais usando o Qdrant. Ele fornece uma interface simples, porém poderosa, para armazenar conteúdo com metadados e recuperá-lo usando consultas em linguagem natural.

Projetado com modularidade e extensibilidade em mente, o Synapstor pode ser usado como:

- 🚀 Servidor MCP (Model Control Protocol) para integração com LLMs
- 🔧 Biblioteca Python para integração em outros projetos
- 🛠️ Suite de ferramentas de linha de comando

## 🏗️ Arquitetura

O Synapstor é organizado em módulos especializados:

```
src/synapstor/
├── embeddings/     # Geradores de embeddings vetoriais
├── mef/            # Matrix Embedding Framework - parser e tipos para UKIs
├── plugins/        # Sistema de plugins extensível
├── tools/          # Utilitários e ferramentas CLI
├── utils/          # Funções auxiliares
├── qdrant.py       # Conector para o banco de dados Qdrant
├── settings.py     # Configurações do sistema
├── mcp_server.py   # Implementação do servidor MCP
└── ...
```

## 🧩 Componentes Principais

### 🔄 Conector Qdrant (`qdrant.py`)

Interface para o banco de dados vetorial Qdrant, gerenciando o armazenamento e recuperação de informações.

```python
from synapstor.qdrant import QdrantConnector, Entry

# Inicializar o conector
connector = QdrantConnector(
    qdrant_url="http://localhost:6333",
    qdrant_api_key=None,
    collection_name="minha_colecao",
    embedding_provider=embedding_provider
)

# Armazenar informações
entry = Entry(
    content="Conteúdo a ser armazenado",
    metadata={"chave": "valor"}
)
await connector.store(entry)

# Buscar informações
resultados = await connector.search("consulta em linguagem natural")
```

### 🧠 Provedores de Embeddings (`embeddings/`)

Implementações para gerar vetores de embedding a partir de texto utilizando diferentes modelos e bibliotecas.

```python
from synapstor.embeddings.factory import create_embedding_provider
from synapstor.settings import EmbeddingProviderSettings

# Criar provedor de embeddings
settings = EmbeddingProviderSettings()
embedding_provider = create_embedding_provider(settings)

# Gerar embeddings
embeddings = await embedding_provider.embed_documents(["Texto de exemplo"])
```

### 📊 Matrix Embedding Framework (`mef/`)

Sistema para estruturar conhecimento em UKIs (Units of Knowledge Interlinked) com metadados semânticos padronizados.

```python
from synapstor.mef import MEFParser
from synapstor.settings import MEFSettings

# Configurar MEF
settings = MEFSettings(
    enabled=True,
    enforce_structure=True
)

# Processar arquivos UKI
parser = MEFParser()
uki_data = parser.parse_file("knowledge/api-auth-pattern.yaml")

# Validar estrutura
if parser.validate_structure(uki_data):
    print(f"UKI válida: {uki_data.title}")
```

### ⚙️ Sistema de Plugins (`plugins/`)

Arquitetura extensível para adicionar novas funcionalidades sem modificar o código principal.

```python
# Em um arquivo tool_minha_ferramenta.py
async def minha_ferramenta(ctx, parametro: str) -> str:
    return f"Processado: {parametro}"

def setup_tools(server):
    server.add_tool(
        minha_ferramenta,
        name="minha-ferramenta",
        description="Descrição da ferramenta"
    )
    return ["minha-ferramenta"]
```

### 🛠️ Ferramentas (`tools/`)

Utilitários e ferramentas de linha de comando, incluindo o poderoso indexador para processamento em lote.

```bash
# Indexar um projeto completo
python -m synapstor.tools.indexer --project meu-projeto --path /caminho/do/projeto

# Indexar com suporte MEF
python -m synapstor.tools.indexer --project meu-projeto --path /caminho/do/projeto --mef-enabled
```

### 🔧 Utilitários (`utils/`)

Funções auxiliares usadas em diferentes partes do sistema.

```python
from synapstor.utils import gerar_id_determinista

# Gerar ID determinístico para evitar duplicações
metadata = {
    "projeto": "meu-projeto",
    "caminho_absoluto": "/caminho/completo/arquivo.txt"
}
id_documento = gerar_id_determinista(metadata)
```

### 🖥️ Servidor MCP (`mcp_server.py`)

Implementação do protocolo Model Control Protocol para integração com LLMs.

```python
from synapstor.mcp_server import QdrantMCPServer
from synapstor.settings import QdrantSettings, EmbeddingProviderSettings, ToolSettings

# Inicializar o servidor
server = QdrantMCPServer(
    tool_settings=ToolSettings(),
    qdrant_settings=QdrantSettings(),
    embedding_provider_settings=EmbeddingProviderSettings(),
    name="synapstor-server"
)

# Executar o servidor
server.run()
```

## ⚡ Uso Rápido

### Instalação

```bash
pip install synapstor
```

### Configuração

Configure o Synapstor através de variáveis de ambiente ou arquivo `.env`:

```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=sua-chave-api
COLLECTION_NAME=synapstor
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Matrix Embedding Framework (MEF)
MEF_ENABLED=true
MEF_ENFORCE_STRUCTURE=true
```

### Servidor MCP

```bash
# Iniciar o servidor MCP
python -m synapstor

# Ou usando o CLI
synapstor-server
```

### Ferramentas CLI

```bash
# Indexar um projeto
synapstor-indexer --project meu-projeto --path /caminho/do/projeto

# Interface centralizada
synapstor-ctl indexer --project meu-projeto --path /caminho/do/projeto
```

## 🧪 Testes

O Synapstor inclui testes abrangentes para garantir a qualidade e robustez:

```bash
# Executar todos os testes
pytest tests/

# Executar testes específicos
pytest tests/test_qdrant_integration.py
```

## 📦 Dependências Principais

- **qdrant-client**: Cliente Python para o banco de dados vetorial Qdrant
- **fastembed**: Biblioteca leve e eficiente para geração de embeddings
- **pydantic**: Validação de dados e configurações
- **mcp**: Implementação do Model Control Protocol

## 🤝 Contribuição

Contribuições são bem-vindas! Veja o [CONTRIBUTING.md](../CONTRIBUTING.md) para diretrizes detalhadas.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](../LICENSE) para detalhes.

---

<a name="english"></a>
# English 🇺🇸

> Modular library for semantic storage and retrieval of information using vector embeddings.

## 🔍 Overview

Synapstor is a modular system for storing and retrieving information based on vector embeddings using Qdrant. It provides a simple yet powerful interface for storing content with metadata and retrieving it using natural language queries.

Designed with modularity and extensibility in mind, Synapstor can be used as:

- 🚀 MCP (Model Control Protocol) server for integration with LLMs
- 🔧 Python library for integration in other projects
- 🛠️ Command-line tools suite

## 🏗️ Architecture

Synapstor is organized into specialized modules:

```
src/synapstor/
├── embeddings/     # Vector embedding generators
├── mef/            # Matrix Embedding Framework - parser and types for UKIs
├── plugins/        # Extensible plugin system
├── tools/          # Utilities and CLI tools
├── utils/          # Helper functions
├── qdrant.py       # Connector for Qdrant database
├── settings.py     # System configurations
├── mcp_server.py   # MCP server implementation
└── ...
```

## 🧩 Main Components

### 🔄 Qdrant Connector (`qdrant.py`)

Interface for the Qdrant vector database, managing storage and retrieval of information.

```python
from synapstor.qdrant import QdrantConnector, Entry

# Initialize the connector
connector = QdrantConnector(
    qdrant_url="http://localhost:6333",
    qdrant_api_key=None,
    collection_name="my_collection",
    embedding_provider=embedding_provider
)

# Store information
entry = Entry(
    content="Content to be stored",
    metadata={"key": "value"}
)
await connector.store(entry)

# Search for information
results = await connector.search("natural language query")
```

### 🧠 Embedding Providers (`embeddings/`)

Implementations to generate embedding vectors from text using different models and libraries.

```python
from synapstor.embeddings.factory import create_embedding_provider
from synapstor.settings import EmbeddingProviderSettings

# Create embedding provider
settings = EmbeddingProviderSettings()
embedding_provider = create_embedding_provider(settings)

# Generate embeddings
embeddings = await embedding_provider.embed_documents(["Example text"])
```

### 📊 Matrix Embedding Framework (`mef/`)

System for structuring knowledge into UKIs (Units of Knowledge Interlinked) with standardized semantic metadata.

```python
from synapstor.mef import MEFParser
from synapstor.settings import MEFSettings

# Configure MEF
settings = MEFSettings(
    enabled=True,
    enforce_structure=True
)

# Process UKI files
parser = MEFParser()
uki_data = parser.parse_file("knowledge/api-auth-pattern.yaml")

# Validate structure
if parser.validate_structure(uki_data):
    print(f"Valid UKI: {uki_data.title}")
```

### ⚙️ Plugin System (`plugins/`)

Extensible architecture for adding new functionalities without modifying the core code.

```python
# In a file tool_my_tool.py
async def my_tool(ctx, parameter: str) -> str:
    return f"Processed: {parameter}"

def setup_tools(server):
    server.add_tool(
        my_tool,
        name="my-tool",
        description="Tool description"
    )
    return ["my-tool"]
```

### 🛠️ Tools (`tools/`)

Utilities and command-line tools, including the powerful indexer for batch processing.

```bash
# Index a complete project
python -m synapstor.tools.indexer --project my-project --path /path/to/project

# Index with MEF support
python -m synapstor.tools.indexer --project my-project --path /path/to/project --mef-enabled
```

### 🔧 Utilities (`utils/`)

Helper functions used in different parts of the system.

```python
from synapstor.utils import generate_deterministic_id

# Generate deterministic ID to avoid duplications
metadata = {
    "project": "my-project",
    "absolute_path": "/complete/path/file.txt"
}
document_id = generate_deterministic_id(metadata)
```

### 🖥️ MCP Server (`mcp_server.py`)

Implementation of the Model Control Protocol for integration with LLMs.

```python
from synapstor.mcp_server import QdrantMCPServer
from synapstor.settings import QdrantSettings, EmbeddingProviderSettings, ToolSettings

# Initialize the server
server = QdrantMCPServer(
    tool_settings=ToolSettings(),
    qdrant_settings=QdrantSettings(),
    embedding_provider_settings=EmbeddingProviderSettings(),
    name="synapstor-server"
)

# Run the server
server.run()
```

## ⚡ Quick Usage

### Installation

```bash
pip install synapstor
```

### Configuration

Configure Synapstor through environment variables or a `.env` file:

```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-api-key
COLLECTION_NAME=synapstor
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Matrix Embedding Framework (MEF)
MEF_ENABLED=true
MEF_ENFORCE_STRUCTURE=true
```

### MCP Server

```bash
# Start the MCP server
python -m synapstor

# Or using the CLI
synapstor-server
```

### CLI Tools

```bash
# Index a project
synapstor-indexer --project my-project --path /path/to/project

# Centralized interface
synapstor-ctl indexer --project my-project --path /path/to/project
```

## 🧪 Tests

Synapstor includes comprehensive tests to ensure quality and robustness:

```bash
# Run all tests
pytest tests/

# Run specific tests
pytest tests/test_qdrant_integration.py
```

## 📦 Main Dependencies

- **qdrant-client**: Python client for the Qdrant vector database
- **fastembed**: Lightweight and efficient library for generating embeddings
- **pydantic**: Data validation and configuration
- **mcp**: Implementation of the Model Control Protocol

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
