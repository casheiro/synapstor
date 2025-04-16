# Synapstor

![Synapstor](https://via.placeholder.com/800x200?text=Synapstor)

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