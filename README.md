# Synapstor 📚🔍

<p align="center">
  <img src="https://2.gravatar.com/userimage/264864229/4e133a67b7d5fff345dd8f2bc4d0743b?size=400" alt="Synapstor" width="400"/>
</p>

![Version](https://img.shields.io/pypi/v/synapstor)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/licença-MIT-green)

## 🌎 Idioma / Language

- [Português 🇧🇷](#português)
- [English 🇺🇸](#english)

---

<a name="português"></a>
# Português 🇧🇷

> **Synapstor** é uma biblioteca modular para armazenamento e recuperação semântica de informações usando embeddings vetoriais e banco de dados Qdrant.
>
> **Nota**: O Synapstor é uma evolução não oficial do projeto [mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant), expandindo suas funcionalidades para criar uma solução mais abrangente para armazenamento e recuperação semântica.


## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Ferramentas CLI](#-ferramentas-cli)
- [Uso Rápido](#-uso-rápido)
- [Integração com LLMs](#-integração-com-llms)
- [Deployment com Docker](#-deployment-com-docker)
- [Documentação Detalhada](#-documentação-detalhada)
- [Testes](#-testes)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## 🔭 Visão Geral

Synapstor é uma solução completa para armazenamento e recuperação de informações baseada em embeddings vetoriais. Combinando a potência do Qdrant (banco de dados vetorial) com modelos modernos de embeddings, o Synapstor permite:

- 🔍 **Busca semântica** em documentos, código e outros conteúdos textuais
- 🧠 **Armazenamento eficiente** de informações com metadados associados
- 🔄 **Integração com LLMs** através do Protocolo MCP (Model Control Protocol)
- 🛠️ **Ferramentas CLI** para indexação e consulta de dados

O projeto foi desenhado com modularidade e extensibilidade em mente, permitindo fácil customização e ampliação de suas capacidades.

## 🏗️ Arquitetura

A estrutura real do projeto é organizada da seguinte forma:

```
synapstor/
├── src/
│   └── synapstor/           # Pacote principal
│       ├── embeddings/      # Geradores de embeddings vetoriais
│       ├── plugins/         # Sistema de plugins extensível
│       ├── tools/           # Utilitários e ferramentas CLI
│       ├── utils/           # Funções auxiliares
│       ├── qdrant.py        # Conector para o banco de dados Qdrant
│       ├── settings.py      # Configurações do sistema
│       ├── mcp_server.py    # Implementação do servidor MCP
│       ├── main.py          # Ponto de entrada principal
│       ├── server.py        # Implementação do servidor
│       └── env_loader.py    # Carregador de variáveis de ambiente
├── tests/                   # Testes automatizados
└── pyproject.toml           # Configuração do projeto e dependências
```

## 🖥️ Requisitos

### Dependências Principais

- **Python**: 3.10 ou superior
- **Qdrant**: Banco de dados vetorial para armazenamento e busca de embeddings
- **Modelos de Embedding**: Por padrão, usa modelos da biblioteca FastEmbed

### Requisitos para o Qdrant

O Synapstor funciona com o Qdrant de duas formas:

1. **Qdrant Cloud** (Recomendado para produção):
   - Crie uma conta em [cloud.qdrant.io](https://cloud.qdrant.io/)
   - Obtenha sua URL e chave API
   - Configure o Synapstor com estas credenciais

2. **Qdrant Local** (Recomendado para desenvolvimento):
   - **Docker** (mais simples):
     ```bash
     docker pull qdrant/qdrant
     docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
     ```
   - **Instalação nativa**: Consulte a [documentação oficial do Qdrant](https://qdrant.tech/documentation/guides/installation/)

## 📦 Instalação

### Ambiente Virtual (Recomendado)

É altamente recomendado usar um ambiente virtual para evitar conflitos de dependências.

#### Usando Conda (Recomendado)

```bash
# Instalar Conda (se ainda não tiver)
# Visite https://docs.conda.io/en/latest/miniconda.html

# Criar ambiente virtual
conda create -n synapstor python=3.10
conda activate synapstor

# Clone o repositório
git clone https://github.com/casheiro/synapstor.git
cd synapstor

# Instalação básica (apenas pacote principal)
pip install -e .

# Instalação para desenvolvimento (inclui formatadores e linters)
pip install -e ".[dev]"

# Instalação para testes (inclui pytest e plugins)
pip install -e ".[test]"

# Instalação completa (desenvolvimento, testes e recursos opcionais)
pip install -e ".[all]"
```

#### Usando venv

```bash
# Criar ambiente virtual
python -m venv synapstor-env
source synapstor-env/bin/activate  # Linux/macOS
# ou
synapstor-env\Scripts\activate  # Windows

# Clone o repositório
git clone https://github.com/casheiro/synapstor.git
cd synapstor

# Instalação básica (apenas pacote principal)
pip install -e .

# Instalação para desenvolvimento (inclui formatadores e linters)
pip install -e ".[dev]"

# Instalação para testes (inclui pytest e plugins)
pip install -e ".[test]"

# Instalação completa (desenvolvimento, testes e recursos opcionais)
pip install -e ".[all]"
```

### Instalação via PyPI (para usuários)

```bash
# Instalação básica
pip install synapstor

# Com suporte a fastembed (recomendado para embeddings rápidos)
pip install "synapstor[fastembed]"
```

### Instalação de Dependências de Desenvolvimento

Se você precisa executar testes ou contribuir com o desenvolvimento, instale as dependências de teste manualmente:

```bash
# Dentro do diretório do projeto, com ambiente virtual ativado
pip install pytest pytest-cov
```

## 🔧 Ferramentas CLI

O Synapstor oferece um conjunto de ferramentas de linha de comando para facilitar seu uso. A forma mais recomendada de interagir com o Synapstor é através do comando centralizado `synapstor-ctl`.

### `synapstor-ctl` (Recomendado)

Interface centralizada para gerenciar todas as funcionalidades do Synapstor:

```bash
# Iniciar o servidor MCP
synapstor-ctl start --transport sse

# Configuração interativa
synapstor-ctl setup

# Indexar um projeto
synapstor-ctl indexer --project my-project --path /path/to/project

# Verificar status
synapstor-ctl status

# Parar o servidor MCP
synapstor-ctl stop

# Reindexar um projeto
synapstor-ctl reindex --project my-project --path /path/to/project

# Exibir logs
synapstor-ctl logs

# Ajuda sobre comandos disponíveis
synapstor-ctl --help
```

### Ferramentas Individuais

Além do `synapstor-ctl`, você também pode usar as ferramentas individuais:

#### `synapstor-server`

Inicia o servidor MCP para integração com LLMs e outras ferramentas.

```bash
# Uso básico
synapstor-server

# Especificar protocolo de transporte
synapstor-server --transport sse

# Especificar arquivo .env personalizado
synapstor-server --env-file config.env
```

#### `synapstor-indexer`

Ferramenta para indexação em lote de projetos e diretórios no Qdrant.

```bash
# Indexar um projeto completo
synapstor-indexer --project meu-projeto --path /caminho/do/projeto

# Opções avançadas
synapstor-indexer --project meu-projeto --path /caminho/do/projeto \
  --collection colecao-personalizada \
  --workers 8 \
  --max-file-size 5 \
  --verbose

# Indexar e testar com uma consulta
synapstor-indexer --project meu-projeto --path /caminho/do/projeto \
  --query "como implementar autenticação"
```

A ferramenta de indexação oferece funcionalidades avançadas:
- Respeito a regras `.gitignore` para exclusão de arquivos
- Detecção automática de arquivos binários
- Processamento paralelo para indexação rápida
- IDs determinísticos para evitar duplicação de documentos

## 🚀 Uso Rápido

### Configuração

Configure o Synapstor através de variáveis de ambiente ou arquivo `.env`:

```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=sua-chave-api
COLLECTION_NAME=synapstor
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Exemplos de Uso

#### Como servidor MCP

```bash
# Iniciar o servidor MCP com a interface centralizada
synapstor-ctl start

# Ou usando o comando específico
synapstor-server
```

#### Indexação de projetos

```bash
# Indexar um projeto usando a interface centralizada (recomendado)
synapstor-ctl indexer --project meu-projeto --path /caminho/do/projeto

# Ou usando o comando específico
synapstor-indexer --project meu-projeto --path /caminho/do/projeto
```

#### Como biblioteca em aplicações Python

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

## 🤖 Integração com LLMs

O Synapstor implementa o [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction), permitindo integração com diversos modelos de linguagem.

### 1. Integração com Claude (Anthropic)

#### Claude Desktop

Configure o Synapstor no arquivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "synapstor": {
      "command": "synapstor-ctl",
      "args": ["server", "--transport", "stdio"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "minha-colecao",
        "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
      }
    }
  }
}
```

#### Claude Web / API

Inicie o servidor com transporte SSE:

```bash
synapstor-ctl start --transport sse
```

Acesse via API Anthropic usando o endpoint local do Synapstor como provedor MCP.

### 2. Integração com Cursor (Editor de Código)

1. Inicie o servidor MCP:
   ```bash
   synapstor-ctl start --transport sse
   ```

2. Em Cursor, vá para Configurações → Contexto → Adicionar Servidor MCP
3. Configure a URL: `http://localhost:8000/sse`
4. Personalize as descrições de ferramenta para melhor integração com seu fluxo de trabalho

### 3. Integração com Windsurf

Semelhante ao Cursor, configure o Windsurf para usar o endpoint SSE do Synapstor como provedor MCP.

### 4. Integração com Microsoft Copilot

Para integrar com Microsoft Copilot:

1. Inicie o servidor com configurações específicas:
   ```bash
   TOOL_STORE_DESCRIPTION="Armazene trechos de código ou documentação" \
   TOOL_FIND_DESCRIPTION="Busque informações relacionadas à consulta" \
   synapstor-ctl start --transport stdio
   ```

2. Configure o Copilot para usar o Synapstor como provedor de plugins

## 🐳 Deployment com Docker

O Synapstor pode ser facilmente implantado usando Docker, permitindo uma configuração consistente em diferentes ambientes.

### Dockerfile Incluído

O projeto inclui um Dockerfile pré-configurado que:
- Usa Python 3.11 como base
- Clona o repositório do Synapstor
- Configura as dependências necessárias
- Expõe a porta 8000 para o transporte SSE
- Usa `synapstor-ctl` como ponto de entrada

### Construindo a Imagem Docker

```bash
# Na raiz do projeto (onde está o Dockerfile)
docker build -t synapstor .
```

### Executando o Contêiner

```bash
# Executar com as configurações básicas
docker run -p 8000:8000 synapstor

# Executar com variáveis de ambiente personalizadas
docker run -p 8000:8000 \
  -e QDRANT_URL="http://seu-servidor-qdrant:6333" \
  -e QDRANT_API_KEY="sua-chave-api" \
  -e COLLECTION_NAME="sua-colecao" \
  -e EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \
  synapstor
```

### Conectando a um Qdrant Externo

Para conectar o contêiner Synapstor a um Qdrant executando em outro contêiner ou serviço:

```bash
# Criar uma rede Docker
docker network create synapstor-network

# Executar o Qdrant
docker run -d --name qdrant --network synapstor-network \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Executar o Synapstor conectado ao Qdrant
docker run -d --name synapstor --network synapstor-network \
  -p 8000:8000 \
  -e QDRANT_URL="http://qdrant:6333" \
  -e COLLECTION_NAME="synapstor" \
  synapstor
```

### Docker Compose (Recomendado para Desenvolvimento)

Para uma configuração completa com Qdrant e Synapstor, você pode usar Docker Compose:

```yaml
# docker-compose.yml
version: '3'

services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    networks:
      - synapstor-network

  synapstor:
    build: .
    ports:
      - "8000:8000"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - COLLECTION_NAME=synapstor
      - EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
    depends_on:
      - qdrant
    networks:
      - synapstor-network

networks:
  synapstor-network:
```

Para usar:

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar todos os serviços
docker-compose down
```

## 📚 Documentação Detalhada

O Synapstor possui documentação específica para cada módulo:

- **[Módulo Principal](src/synapstor/README.md)**: Visão geral e componentes principais
- **[Embeddings](src/synapstor/embeddings/README.md)**: Geração de embeddings vetoriais
- **[Plugins](src/synapstor/plugins/README.md)**: Sistema extensível de plugins
- **[Ferramentas](src/synapstor/tools/README.md)**: Ferramentas CLI e utilitários
- **[Utilitários](src/synapstor/utils/README.md)**: Funções auxiliares comuns
- **[Testes](tests/README.md)**: Suíte de testes e exemplos

## 🧪 Testes

O Synapstor inclui uma suíte completa de testes para garantir a qualidade e robustez do código:

```bash
# Com ambiente virtual ativado e dependências de teste instaladas (pip install -e ".[test]")

# Executar todos os testes
pytest

# Executar um módulo específico de testes
pytest tests/test_qdrant_integration.py

# Executar com cobertura de código
pytest --cov=synapstor
```

### Integração Contínua

O projeto utiliza GitHub Actions para automatizar testes, verificações de qualidade de código e publicação:

- **Testes Automatizados**: Executa os testes em múltiplas versões do Python (3.10, 3.11, 3.12)
- **Pre-commit Checks**: Verifica formatação, linting e tipagem estática
- **Publicação de Pacotes**: Automatiza o processo de publicação no PyPI

Você pode ver os detalhes nas configurações em `.github/workflows/`.

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir para o Synapstor:

1. Faça um fork do projeto
2. Configure seu ambiente de desenvolvimento:
   ```bash
   # Clone seu fork
   git clone https://github.com/seu-usuario/synapstor.git
   cd synapstor

   # Instale as dependências de desenvolvimento
   pip install -e ".[dev,test]"

   # Configure o pre-commit
   pre-commit install
   ```
3. Crie uma branch para sua feature (`git checkout -b feature/nome-da-feature`)
4. Faça suas alterações seguindo as convenções do projeto
5. Execute os testes para garantir que tudo está funcionando (`pytest`)
6. Faça commit e push das alterações (`git push origin feature/nome-da-feature`)
7. Abra um Pull Request descrevendo suas alterações

### Fluxo de Desenvolvimento

- Mantenha os commits pequenos e focados
- Escreva testes para novas funcionalidades
- Siga o estilo de código do projeto (enforçado pelo pre-commit)
- Mantenha a documentação atualizada
- Atualize o CHANGELOG.md para novas versões

## 📝 Conventional Commits e CHANGELOG Automático

O Synapstor utiliza o padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/) para automatizar a geração de versões e do CHANGELOG.

### Estrutura das Mensagens de Commit

Cada mensagem de commit deve seguir o seguinte formato:

```
<tipo>(<escopo opcional>): <descrição>

<corpo opcional>

<rodapé opcional>
```

#### Tipos de Commits

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Formatação, ponto e vírgula ausente, etc; sem alteração de código
- `refactor`: Refatoração de código sem alterar funcionalidade
- `test`: Adicionando testes ausentes ou corrigindo testes existentes
- `chore`: Alterações no processo de build, ferramentas auxiliares, etc
- `perf`: Mudanças que melhoram performance

#### Commits de Breaking Change

Para indicar uma mudança que quebra compatibilidade, adicione um `!` após o tipo/escopo ou adicione `BREAKING CHANGE:` no corpo ou rodapé:

```
feat!: alteração que quebra compatibilidade

# OU

feat: nova funcionalidade

BREAKING CHANGE: explica o que quebra e por quê
```

### Geração de Versão Automática

O semantic-release usa estas convenções para determinar automaticamente:

1. **MAJOR** (1.0.0): Quando há commits com `BREAKING CHANGE`
2. **MINOR** (0.1.0): Quando há commits do tipo `feat`
3. **PATCH** (0.0.1): Quando há commits do tipo `fix`

### Exemplos Práticos

```
feat: adiciona opção de busca por metadados
fix: corrige problema na indexação de arquivos grandes
docs: atualiza documentação da API
feat(server): adiciona novo endpoint para estatísticas
fix!: remove suporte a Python 3.9
```

### CHANGELOG

O CHANGELOG.md é gerado automaticamente quando uma nova versão é criada. Este arquivo contém todas as alterações relevantes organizadas por versão, facilitando o acompanhamento da evolução do projeto.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  Desenvolvido com ❤️ pelo time Synapstor by <a href="https://github.com/casheiro">Casheiro®</a>
</p>

<a name="english"></a>
# English 🇺🇸

> **Synapstor** is a modular library for semantic storage and retrieval of information using vector embeddings and the Qdrant database.
>
> **Note**: Synapstor is an unofficial evolution of the [mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant) project, expanding its functionality to create a more comprehensive solution for semantic storage and retrieval.


## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [CLI Tools](#-cli-tools)
- [Quick Usage](#-quick-usage)
- [LLM Integration](#-llm-integration)
- [Docker Deployment](#-docker-deployment)
- [Detailed Documentation](#-detailed-documentation)
- [Tests](#-tests)
- [Contributing](#-contributing)
- [License](#-license)

## 🔭 Overview

Synapstor is a complete solution for storing and retrieving information based on vector embeddings. Combining the power of Qdrant (vector database) with modern embedding models, Synapstor allows:

- 🔍 **Semantic search** in documents, code, and other textual content
- 🧠 **Efficient storage** of information with associated metadata
- 🔄 **Integration with LLMs** through the MCP (Model Control Protocol)
- 🛠️ **CLI tools** for indexing and querying data

The project was designed with modularity and extensibility in mind, allowing easy customization and expansion of its capabilities.

## 🏗️ Architecture

The actual structure of the project is organized as follows:

```
synapstor/
├── src/
│   └── synapstor/           # Main package
│       ├── embeddings/      # Vector embedding generators
│       ├── plugins/         # Extensible plugin system
│       ├── tools/           # Utilities and CLI tools
│       ├── utils/           # Helper functions
│       ├── qdrant.py        # Connector for Qdrant database
│       ├── settings.py      # System configurations
│       ├── mcp_server.py    # MCP server implementation
│       ├── main.py          # Main entry point
│       ├── server.py        # Server implementation
│       └── env_loader.py    # Environment variable loader
├── tests/                   # Automated tests
└── pyproject.toml           # Project configuration and dependencies
```

## 🖥️ Requirements

### Main Dependencies

- **Python**: 3.10 or higher
- **Qdrant**: Vector database for storing and searching embeddings
- **Embedding Models**: By default, uses models from the FastEmbed library

### Qdrant Requirements

Synapstor works with Qdrant in two ways:

1. **Qdrant Cloud** (Recommended for production):
   - Create an account at [cloud.qdrant.io](https://cloud.qdrant.io/)
   - Get your URL and API key
   - Configure Synapstor with these credentials

2. **Local Qdrant** (Recommended for development):
   - **Docker** (simpler):
     ```bash
     docker pull qdrant/qdrant
     docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
     ```
   - **Native installation**: See the [official Qdrant documentation](https://qdrant.tech/documentation/guides/installation/)

## 📦 Installation

### Virtual Environment (Recommended)

It's highly recommended to use a virtual environment to avoid dependency conflicts.

#### Using Conda (Recommended)

```bash
# Install Conda (if you don't have it yet)
# Visit https://docs.conda.io/en/latest/miniconda.html

# Create virtual environment
conda create -n synapstor python=3.10
conda activate synapstor

# Clone the repository
git clone https://github.com/casheiro/synapstor.git
cd synapstor

# Basic installation (main package only)
pip install -e .

# Development installation (includes formatters and linters)
pip install -e ".[dev]"

# Test installation (includes pytest and plugins)
pip install -e ".[test]"

# Complete installation (development, tests, and optional features)
pip install -e ".[all]"
```

#### Using venv

```bash
# Create virtual environment
python -m venv synapstor-env
source synapstor-env/bin/activate  # Linux/macOS
# or
synapstor-env\Scripts\activate  # Windows

# Clone the repository
git clone https://github.com/casheiro/synapstor.git
cd synapstor

# Basic installation (main package only)
pip install -e .

# Development installation (includes formatters and linters)
pip install -e ".[dev]"

# Test installation (includes pytest and plugins)
pip install -e ".[test]"

# Complete installation (development, tests, and optional features)
pip install -e ".[all]"
```

### Installation via PyPI (for users)

```bash
# Basic installation
pip install synapstor

# With fastembed support (recommended for fast embeddings)
pip install "synapstor[fastembed]"
```

### Installing Development Dependencies

If you need to run tests or contribute to development, manually install the test dependencies:

```bash
# Inside the project directory, with virtual environment activated
pip install pytest pytest-cov
```

## 🔧 CLI Tools

Synapstor offers a set of command-line tools to facilitate its use. The most recommended way to interact with Synapstor is through the centralized `synapstor-ctl` command.

### `synapstor-ctl` (Recommended)

Centralized interface to manage all Synapstor functionalities:

```bash
# Start the MCP server
synapstor-ctl start

# Interactive configuration
synapstor-ctl setup

# Index a project
synapstor-ctl indexer --project my-project --path /path/to/project

# View status
synapstor-ctl status

# Stop the MCP server
synapstor-ctl stop

# Reindex a project
synapstor-ctl reindex --project my-project --path /path/to/project

# Show logs
synapstor-ctl logs

# Help on available commands
synapstor-ctl --help
```

### Individual Tools

In addition to `synapstor-ctl`, you can also use the individual tools:

#### `synapstor-server`

Starts the MCP server for integration with LLMs and other tools.

```bash
# Basic usage
synapstor-server

# Specify transport protocol
synapstor-server --transport sse

# Specify custom .env file
synapstor-server --env-file config.env
```

#### `synapstor-indexer`

Tool for batch indexing of projects and directories in Qdrant.

```bash
# Index a complete project
synapstor-indexer --project my-project --path /path/to/project

# Advanced options
synapstor-indexer --project my-project --path /path/to/project \
  --collection custom-collection \
  --workers 8 \
  --max-file-size 5 \
  --verbose

# Index and test with a query
synapstor-indexer --project my-project --path /path/to/project \
  --query "how to implement authentication"
```

The indexing tool offers advanced features:
- Respect for `.gitignore` rules for file exclusion
- Automatic detection of binary files
- Parallel processing for fast indexing
- Deterministic IDs to avoid document duplication

## 🚀 Quick Usage

### Configuration

Configure Synapstor through environment variables or a `.env` file:

```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-api-key
COLLECTION_NAME=synapstor
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Usage Examples

#### As an MCP server

```bash
# Start the MCP server with the centralized interface
synapstor-ctl start

# Or using the specific command
synapstor-server
```

#### Project indexing

```bash
# Index a project using the centralized interface (recommended)
synapstor-ctl indexer --project my-project --path /path/to/project

# Or using the specific command
synapstor-indexer --project my-project --path /path/to/project
```

#### As a library in Python applications

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

## 🤖 LLM Integration

Synapstor implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction), allowing integration with various language models.

### 1. Integration with Claude (Anthropic)

#### Claude Desktop

Configure Synapstor in the `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "synapstor": {
      "command": "synapstor-ctl",
      "args": ["server", "--transport", "stdio"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "my-collection",
        "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
      }
    }
  }
}
```

#### Claude Web / API

Start the server with SSE transport:

```bash
synapstor-ctl start --transport sse
```

Access via Anthropic API using Synapstor's local endpoint as an MCP provider.

### 2. Integration with Cursor (Code Editor)

1. Start the MCP server:
   ```bash
   synapstor-ctl start --transport sse
   ```

2. In Cursor, go to Settings → Context → Add MCP Server
3. Configure the URL: `http://localhost:8000/sse`
4. Customize tool descriptions for better integration with your workflow

### 3. Integration with Windsurf

Similar to Cursor, configure Windsurf to use Synapstor's SSE endpoint as an MCP provider.

### 4. Integration with Microsoft Copilot

To integrate with Microsoft Copilot:

1. Start the server with specific configurations:
   ```bash
   TOOL_STORE_DESCRIPTION="Store code snippets or documentation" \
   TOOL_FIND_DESCRIPTION="Find information related to the query" \
   synapstor-ctl start --transport stdio
   ```

2. Configure Copilot to use Synapstor as a plugin provider

## 🐳 Docker Deployment

Synapstor can be easily deployed using Docker, allowing consistent configuration across different environments.

### Included Dockerfile

The project includes a pre-configured Dockerfile that:
- Uses Python 3.11 as a base
- Clones the Synapstor repository
- Sets up the necessary dependencies
- Exposes port 8000 for SSE transport
- Uses `synapstor-ctl` as the entry point

### Building the Docker Image

```bash
# At the project root (where the Dockerfile is)
docker build -t synapstor .
```

### Running the Container

```bash
# Run with basic settings
docker run -p 8000:8000 synapstor

# Run with custom environment variables
docker run -p 8000:8000 \
  -e QDRANT_URL="http://your-qdrant-server:6333" \
  -e QDRANT_API_KEY="your-api-key" \
  -e COLLECTION_NAME="your-collection" \
  -e EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \
  synapstor
```

### Connecting to an External Qdrant

To connect the Synapstor container to a Qdrant running in another container or service:

```bash
# Create a Docker network
docker network create synapstor-network

# Run Qdrant
docker run -d --name qdrant --network synapstor-network \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Run Synapstor connected to Qdrant
docker run -d --name synapstor --network synapstor-network \
  -p 8000:8000 \
  -e QDRANT_URL="http://qdrant:6333" \
  -e COLLECTION_NAME="synapstor" \
  synapstor
```

### Docker Compose (Recommended for Development)

For a complete setup with Qdrant and Synapstor, you can use Docker Compose:

```yaml
# docker-compose.yml
version: '3'

services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    networks:
      - synapstor-network

  synapstor:
    build: .
    ports:
      - "8000:8000"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - COLLECTION_NAME=synapstor
      - EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
    depends_on:
      - qdrant
    networks:
      - synapstor-network

networks:
  synapstor-network:
```

To use:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 📚 Detailed Documentation

Synapstor has specific documentation for each module:

- **[Main Module](src/synapstor/README.md)**: Overview and main components
- **[Embeddings](src/synapstor/embeddings/README.md)**: Vector embedding generation
- **[Plugins](src/synapstor/plugins/README.md)**: Extensible plugin system
- **[Tools](src/synapstor/tools/README.md)**: CLI tools and utilities
- **[Utilities](src/synapstor/utils/README.md)**: Common helper functions
- **[Tests](tests/README.md)**: Test suite and examples

## 🧪 Tests

Synapstor includes a complete test suite to ensure code quality and robustness:

```bash
# With virtual environment activated and test dependencies installed (pip install -e ".[test]")

# Run all tests
pytest

# Run a specific test module
pytest tests/test_qdrant_integration.py

# Run with code coverage
pytest --cov=synapstor
```

### Continuous Integration

The project uses GitHub Actions to automate tests, code quality checks, and publishing:

- **Automated Tests**: Runs tests on multiple Python versions (3.10, 3.11, 3.12)
- **Pre-commit Checks**: Checks formatting, linting, and static typing
- **Package Publishing**: Automates the process of publishing to PyPI

You can see the details in the configurations in `.github/workflows/`.

## 🤝 Contributing

Contributions are welcome! To contribute to Synapstor:

1. Fork the project
2. Set up your development environment:
   ```bash
   # Clone your fork
   git clone https://github.com/your-username/synapstor.git
   cd synapstor

   # Install development dependencies
   pip install -e ".[dev,test]"

   # Configure pre-commit
   pre-commit install
   ```
3. Create a branch for your feature (`git checkout -b feature/feature-name`)
4. Make your changes following the project conventions
5. Run tests to ensure everything is working (`pytest`)
6. Commit and push your changes (`git push origin feature/feature-name`)
7. Open a Pull Request describing your changes

### Development Flow

- Keep commits small and focused
- Write tests for new features
- Follow the project's code style (enforced by pre-commit)
- Keep documentation up to date
- Update CHANGELOG.md for new versions

## 📝 Conventional Commits and Automated CHANGELOG

Synapstor uses the [Conventional Commits](https://www.conventionalcommits.org/) pattern to automate version generation and CHANGELOG updates.

### Commit Message Structure

Each commit message should follow this format:

```
<type>(<optional scope>): <description>

<optional body>

<optional footer>
```

#### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc; no code change
- `refactor`: Code refactoring without changing functionality
- `test`: Adding missing tests or fixing existing tests
- `chore`: Changes to build process, auxiliary tools, etc
- `perf`: Performance improvements

#### Breaking Change Commits

To indicate a breaking change, add a `!` after the type/scope or add `BREAKING CHANGE:` in the body or footer:

```
feat!: breaking change

# OR

feat: new feature

BREAKING CHANGE: explain what breaks and why
```

### Automated Version Generation

Semantic-release uses these conventions to automatically determine:

1. **MAJOR** (1.0.0): When there are commits with `BREAKING CHANGE`
2. **MINOR** (0.1.0): When there are commits of type `feat`
3. **PATCH** (0.0.1): When there are commits of type `fix`

### Practical Examples

```
feat: add metadata search option
fix: resolve large file indexing issue
docs: update API documentation
feat(server): add new endpoint for statistics
fix!: remove support for Python 3.9
```

### CHANGELOG

The CHANGELOG.md is automatically generated when a new version is created. This file contains all relevant changes organized by version, making it easy to track the project's evolution.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Developed with ❤️ by the Synapstor team by <a href="https://github.com/casheiro">Casheiro®</a>
</p>
