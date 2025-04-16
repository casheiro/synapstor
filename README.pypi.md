# Synapstor 📚🔍

<p align="center">
  <img src="https://2.gravatar.com/userimage/264864229/4e133a67b7d5fff345dd8f2bc4d0743b?size=400" alt="Synapstor" width="400"/>
</p>

![Version](https://img.shields.io/badge/versão-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/licença-MIT-green)

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
# Instalação via pip
pip install synapstor

# Usar com FastEmbed (recomendado)
pip install "synapstor[fastembed]"
```

## 🚀 Uso Rápido

### Configuração

Configure o Synapstor através de variáveis de ambiente ou arquivo `.env`:

```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=sua-chave-api
COLLECTION_NAME=synapstor
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Como servidor MCP

```bash
# Iniciar o servidor MCP com a interface centralizada
synapstor-ctl server

# Ou usando o comando específico
synapstor-server
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

<p align="center">
  Desenvolvido com ❤️ pelo time Synapstor by <a href="https://github.com/casheiro">Casheiro®</a>
</p> 