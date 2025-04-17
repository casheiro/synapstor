# Synapstor 📚🔍

**Versão 0.1.2 | Python 3.10+ | Licença MIT**

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
   synapstor-ctl server --qdrant-url http://localhost:6333 --qdrant-api-key sua-chave-api --collection-name synapstor --embedding-model "sentence-transformers/all-MiniLM-L6-v2"
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
synapstor-ctl server

# Com parâmetros de configuração
synapstor-ctl server --qdrant-url http://localhost:6333 --qdrant-api-key sua-chave-api --collection-name minha_colecao --embedding-model "sentence-transformers/all-MiniLM-L6-v2"
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

Desenvolvido com ❤️ pelo time Synapstor
