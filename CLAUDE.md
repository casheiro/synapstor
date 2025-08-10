# CLAUDE.md

## 🌎 Idioma / Language

- [Português 🇧🇷](#português)
- [English 🇺🇸](#english)

---

<a name="português"></a>
# Português 🇧🇷

Este arquivo fornece orientações para o Claude Code (claude.ai/code) ao trabalhar com código neste repositório.

## Comandos de Desenvolvimento Comuns

### Instalação e Configuração
```bash
# Instalar ambiente de desenvolvimento completo
pip install -e ".[all]"

# Instalar apenas dependências de teste
pip install -e ".[test]"

# Instalar apenas dependências de desenvolvimento
pip install -e ".[dev]"

# Configurar pre-commit hooks
pre-commit install
```

### Testes
```bash
# Executar todos os testes
pytest

# Executar teses com cobertura
pytest --cov=synapstor

# Executar teste específico
pytest tests/test_qdrant_integration.py

# Executar testes com configuração do GitHub Actions
pytest --maxfail=1 --disable-warnings -q
```

### Qualidade de Código
```bash
# Executar verificações de pre-commit em todos os arquivos
pre-commit run --all-files

# Executar formatação com black
black .

# Executar verificação de tipos com mypy
python -m mypy_runner

# Executar ruff para linting
ruff check --fix
```

### Internacionalização (i18n)
```bash
# Testar sistema de i18n
python examples/i18n_example.py

# Configurar idioma via variável de ambiente
export SYNAPSTOR_LANGUAGE=pt  # Português
export SYNAPSTOR_LANGUAGE=en  # English

# Rodar servidor em português
SYNAPSTOR_LANGUAGE=pt python -m synapstor

# Rodar servidor em inglês
SYNAPSTOR_LANGUAGE=en python -m synapstor
```

### Ferramentas CLI
```bash
# Comando principal de controle
synapstor-ctl start
synapstor-ctl start --transport http --host 0.0.0.0 --port 8000
synapstor-ctl indexer --project nome-projeto --path /caminho/projeto

# Indexar projeto com suporte MEF via synapstor-ctl
synapstor-ctl indexer --project nome-projeto --path /caminho/projeto --mef-enabled
synapstor-ctl indexer --project nome-projeto --path /caminho/projeto -m -e
synapstor-ctl stop

# Iniciar servidor MCP com diferentes transportes
synapstor-server --transport stdio    # Para integração direta com LLMs
synapstor-server --transport sse      # Para Server-Sent Events
synapstor-server --transport http     # Para Streamable HTTP MCP
synapstor-server --transport http --host 0.0.0.0 --port 8000

# Indexar projeto
synapstor-indexer --project meu-projeto --path /caminho/do/projeto

# Indexar projeto com suporte MEF (Matrix Embedding Framework)
synapstor-indexer --project meu-projeto --path /caminho/do/projeto --mef-enabled
synapstor-indexer --project meu-projeto --path /caminho/do/projeto --mef-enabled --mef-enforce-structure

# Versões curtas dos argumentos MEF (mais prático)
synapstor-indexer --project meu-projeto --path /caminho/do/projeto -m
synapstor-indexer --project meu-projeto --path /caminho/do/projeto -m -e
```

### Ferramentas MCP Avançadas
```bash
# Modo Synapstor - Raciocínio Multidisciplinar com RAG Dinâmico
modo-synapstor tema="Inteligência Artificial na Educação"
modo-synapstor tema="Arquitetura de Microserviços" max_personalidades=5

# Informações sobre funcionamento dinâmico
info-modo-synapstor

# Configurar personalidades customizadas
configurar-synapstor tema="Blockchain" personalidades_customizadas='[...]'
```

## Matrix Embedding Framework (MEF)

O Synapstor agora suporta o Matrix Embedding Framework (MEF), uma especificação padronizada para estruturar conhecimento em unidades atômicas chamadas UKIs (Units of Knowledge Interlinked).

### Uso do MEF
```bash
# Ativar MEF via variável de ambiente
export MEF_ENABLED=true
synapstor-indexer --project knowledge-base --path ./knowledge-source

# Ativar MEF via argumentos CLI
synapstor-indexer --project knowledge-base --path ./knowledge-source --mef-enabled

# Modo rigoroso (validação estrutural obrigatória)
synapstor-indexer --project knowledge-base --path ./knowledge-source --mef-enabled --mef-enforce-structure

# Versões curtas (mais prático)
synapstor-indexer --project knowledge-base --path ./knowledge-source -m
synapstor-indexer --project knowledge-base --path ./knowledge-source -m -e
```

### Argumentos MEF - Versões Curtas
Para facilitar o uso, os argumentos MEF possuem versões curtas:
- `--mef-enabled` → `-m` (habilita processamento MEF)
- `--mef-enforce-structure` → `-e` (modo rigoroso, requer `-m`)

### Estrutura MEF
Arquivos YAML com estrutura MEF seguem o padrão:
```yaml
id: unik-technical-api-authentication
title: API Authentication Pattern
domain: technical
type: pattern
context: implementation
content: |
  Este padrão define como implementar autenticação JWT em APIs...
examples:
  - input: Login request with valid credentials
    output: JWT token with 15min expiration
intent_of_use:
  - validate_implementation
  - generate_authentication_code
use_case_stage:
  - implementation
  - peer_review
related_to:
  - unik-technical-jwt-validation
```

### Benefícios MEF
- **Metadados Estruturados**: Informações contextuais automáticas para LLMs
- **Relacionamentos Semânticos**: Links entre UKIs para navegação contextual
- **Busca Aprimorada**: Filtros por domínio, tipo, contexto e intenção de uso
- **Validação Automática**: Verificação de estrutura e consistência
- **Indexação Inteligente**: Conteúdo otimizado para embeddings vetoriais

## Arquitetura do Projeto

### Estrutura Principal
- **src/synapstor/**: Pacote principal do projeto
  - **embeddings/**: Sistema modular de embeddings vetoriais usando FastEmbed e Sentence Transformers
  - **mef/**: Matrix Embedding Framework - parser, validador e tipos para UKIs
  - **plugins/**: Sistema extensível de plugins com ferramentas como tool_changelog e tool_boilerplate
  - **tools/**: Ferramentas CLI, especialmente indexer.py para indexação em lote (com suporte MEF)
  - **utils/**: Utilitários auxiliares como id_generator para IDs determinísticos
  - **qdrant.py**: Conector principal para banco de dados Qdrant
  - **settings.py**: Configurações baseadas em Pydantic Settings (inclui MEFSettings)
  - **mcp_server.py**: Implementação do servidor MCP com formatação MEF-aware
  - **server.py**: Servidor FastAPI para transporte SSE
  - **env_loader.py**: Carregador de variáveis de ambiente

- **cli/**: Interface de linha de comando modular
  - **ctl.py**: Comando principal de controle (synapstor-ctl)
  - **server.py**: Wrapper para iniciar servidor MCP
  - **indexer.py**: Wrapper para indexação
  - **config.py**, **setup.py**, **reindex.py**: Ferramentas auxiliares

### Arquitetura de Embeddings
O sistema usa um padrão Factory para provedores de embeddings:
- **base.py**: Classe abstrata EmbeddingProvider
- **factory.py**: Factory para criar instâncias de provedores
- **fastembed.py**: Implementação usando FastEmbed
- Suporte a Sentence Transformers via configuração

### Sistema de Plugins
- Plugins são descobertos dinamicamente no diretório plugins/
- Cada plugin implementa ferramentas MCP específicas
- **tool_changelog.py**: Gera changelogs automaticamente baseado em Conventional Commits
- **tool_boilerplate.py**: Gera código boilerplate para projetos
- **tool_modo_synapstor.py**: Sistema de raciocínio multidisciplinar com RAG integrado

### Sistema de Internacionalização (i18n)
Suporte completo a múltiplos idiomas:
- **Idiomas Suportados**: Português (pt-BR) e English (en-US)
- **Traduções Automáticas**: Todas as mensagens, descrições e prompts são traduzidos
- **Configuração Flexível**: Via SYNAPSTOR_LANGUAGE ou configuração programática
- **Sistema de Fallback**: Inglês como idioma de fallback automático
- **Thread-Safe**: Sistema seguro para aplicações concorrentes
- **Interpolação**: Suporte a variáveis com `{variavel}` nas traduções

### Configuração e Variáveis de Ambiente
Baseado em Pydantic Settings com validação automática:
- **QdrantSettings**: Configuração do banco Qdrant (URL, API key, coleção)
- **EmbeddingProviderSettings**: Configuração de embeddings (provedor, modelo)
- **ToolSettings**: Configuração de descrições de ferramentas MCP
- **I18nSettings**: Configuração de idioma (SYNAPSTOR_LANGUAGE=pt/en)
- **ServerSettings**: Configuração de servidor HTTP (host, porta, CORS)

### Padrões de ID e Indexação
- IDs determinísticos para evitar duplicação de documentos
- Respeito a regras .gitignore durante indexação
- Processamento paralelo com workers configuráveis
- Detecção automática de arquivos binários

## Integração MCP
O projeto implementa o Model Context Protocol para integração com LLMs:
- **stdio**: Para integração direta com LLMs via stdin/stdout
- **sse**: Para Server-Sent Events, útil para aplicações web
- **http**: Para Streamable HTTP MCP, o novo padrão para servidores HTTP
- Ferramentas básicas de store/find para armazenamento semântico
- **Modo Synapstor**: Sistema avançado de raciocínio multidisciplinar com RAG
- Configuração flexível de descrições de ferramentas via variáveis de ambiente
- Configuração de host/porta para transporte HTTP via .env ou argumentos CLI

## Modo Synapstor - Funcionalidade Avançada
Ferramenta MCP que fornece prompts estruturados para raciocínio multidisciplinar:
- **Instruções Dinâmicas**: Orienta o LLM a gerar especialistas apropriados para cada tema
- **RAG Contextual**: Fornece documentos relevantes recuperados automaticamente do Qdrant
- **Prompts Multifásicos**: Estrutura de duas fases (geração de personalidades + debate)
- **Adaptabilidade Total**: Funciona para qualquer tema sem limitações de domínio
- **Personalidades Customizadas**: Suporte opcional via JSON para casos específicos
- **Arquitetura MCP**: O Synapstor fornece contexto; o LLM executa o raciocínio

## Dependências Principais
- **qdrant-client**: Conectividade com banco vetorial Qdrant
- **fastembed**: Geração rápida de embeddings
- **sentence-transformers**: Modelos de embeddings alternativos
- **mcp[cli]**: Implementação do Model Context Protocol
- **fastapi/uvicorn**: Servidor web para transporte SSE
- **pydantic-settings**: Configuração baseada em tipos

## Convenções de Código
- Usa conventional commits com commitizen
- Formatação com black
- Linting com ruff
- Type checking com mypy (configuração flexível)
- Pre-commit hooks obrigatórios
- Versionamento semântico automático

---

<a name="english"></a>
# English 🇺🇸

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Installation and Configuration
```bash
# Install complete development environment
pip install -e ".[all]"

# Install test dependencies only
pip install -e ".[test]"

# Install development dependencies only
pip install -e ".[dev]"

# Configure pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=synapstor

# Run specific test
pytest tests/test_qdrant_integration.py

# Run tests with GitHub Actions configuration
pytest --maxfail=1 --disable-warnings -q
```

### Code Quality
```bash
# Run pre-commit checks on all files
pre-commit run --all-files

# Run black formatting
black .

# Run type checking with mypy
python -m mypy_runner

# Run ruff for linting
ruff check --fix
```

### Internationalization (i18n)
```bash
# Test i18n system
python examples/i18n_example.py

# Configure language via environment variable
export SYNAPSTOR_LANGUAGE=pt  # Portuguese
export SYNAPSTOR_LANGUAGE=en  # English

# Run server in Portuguese
SYNAPSTOR_LANGUAGE=pt python -m synapstor

# Run server in English
SYNAPSTOR_LANGUAGE=en python -m synapstor
```

### CLI Tools
```bash
# Main control command
synapstor-ctl start
synapstor-ctl start --transport http --host 0.0.0.0 --port 8000
synapstor-ctl indexer --project project-name --path /project/path

# Index project with MEF support via synapstor-ctl
synapstor-ctl indexer --project project-name --path /project/path --mef-enabled
synapstor-ctl indexer --project project-name --path /project/path -m -e
synapstor-ctl stop

# Start MCP server with different transports
synapstor-server --transport stdio    # For direct LLM integration
synapstor-server --transport sse      # For Server-Sent Events
synapstor-server --transport http     # For Streamable HTTP MCP
synapstor-server --transport http --host 0.0.0.0 --port 8000

# Index project
synapstor-indexer --project my-project --path /project/path

# Index project with MEF (Matrix Embedding Framework) support
synapstor-indexer --project my-project --path /project/path --mef-enabled
synapstor-indexer --project my-project --path /project/path --mef-enabled --mef-enforce-structure

# Short versions of MEF arguments (more practical)
synapstor-indexer --project my-project --path /project/path -m
synapstor-indexer --project my-project --path /project/path -m -e
```

### Advanced MCP Tools
```bash
# Modo Synapstor - Multidisciplinary Reasoning with Dynamic RAG
modo-synapstor tema="Artificial Intelligence in Education"
modo-synapstor tema="Microservices Architecture" max_personalidades=5

# Information about dynamic operation
info-modo-synapstor

# Configure custom personalities
configurar-synapstor tema="Blockchain" personalidades_customizadas='[...]'
```

## Matrix Embedding Framework (MEF)

Synapstor now supports the Matrix Embedding Framework (MEF), a standardized specification for structuring knowledge into atomic units called UKIs (Units of Knowledge Interlinked).

### MEF Usage
```bash
# Enable MEF via environment variable
export MEF_ENABLED=true
synapstor-indexer --project knowledge-base --path ./knowledge-source

# Enable MEF via CLI arguments
synapstor-indexer --project knowledge-base --path ./knowledge-source --mef-enabled

# Strict mode (mandatory structural validation)
synapstor-indexer --project knowledge-base --path ./knowledge-source --mef-enabled --mef-enforce-structure

# Short versions (more practical)
synapstor-indexer --project knowledge-base --path ./knowledge-source -m
synapstor-indexer --project knowledge-base --path ./knowledge-source -m -e
```

### MEF Short Arguments
For ease of use, MEF arguments have short versions:
- `--mef-enabled` → `-m` (enables MEF processing)
- `--mef-enforce-structure` → `-e` (strict mode, requires `-m`)

### MEF Structure
YAML files with MEF structure follow this pattern:
```yaml
id: unik-technical-api-authentication
title: API Authentication Pattern
domain: technical
type: pattern
context: implementation
content: |
  This pattern defines how to implement JWT authentication in APIs...
examples:
  - input: Login request with valid credentials
    output: JWT token with 15min expiration
intent_of_use:
  - validate_implementation
  - generate_authentication_code
use_case_stage:
  - implementation
  - peer_review
related_to:
  - unik-technical-jwt-validation
```

### MEF Benefits
- **Structured Metadata**: Automatic contextual information for LLMs
- **Semantic Relationships**: Links between UKIs for contextual navigation
- **Enhanced Search**: Filters by domain, type, context, and intent of use
- **Automatic Validation**: Structure and consistency verification
- **Smart Indexing**: Content optimized for vector embeddings

## Project Architecture

### Main Structure
- **src/synapstor/**: Main project package
  - **embeddings/**: Modular vector embeddings system using FastEmbed and Sentence Transformers
  - **mef/**: Matrix Embedding Framework - parser, validator and types for UKIs
  - **plugins/**: Extensible plugin system with tools like tool_changelog and tool_boilerplate
  - **tools/**: CLI tools, especially indexer.py for batch indexing (with MEF support)
  - **utils/**: Helper utilities like id_generator for deterministic IDs
  - **qdrant.py**: Main connector for Qdrant database
  - **settings.py**: Pydantic Settings-based configuration (includes MEFSettings)
  - **mcp_server.py**: MCP server implementation with MEF-aware formatting
  - **server.py**: FastAPI server for SSE transport
  - **env_loader.py**: Environment variable loader

- **cli/**: Modular command-line interface
  - **ctl.py**: Main control command (synapstor-ctl)
  - **server.py**: Wrapper to start MCP server
  - **indexer.py**: Indexing wrapper
  - **config.py**, **setup.py**, **reindex.py**: Helper tools

### Embeddings Architecture
System uses Factory pattern for embedding providers:
- **base.py**: Abstract EmbeddingProvider class
- **factory.py**: Factory to create provider instances
- **fastembed.py**: Implementation using FastEmbed
- Sentence Transformers support via configuration

### Plugin System
- Plugins are dynamically discovered in the plugins/ directory
- Each plugin implements specific MCP tools
- **tool_changelog.py**: Automatically generates changelogs based on Conventional Commits
- **tool_boilerplate.py**: Generates boilerplate code for projects
- **tool_modo_synapstor.py**: Multidisciplinary reasoning system with integrated RAG

### Internationalization System (i18n)
Complete support for multiple languages:
- **Supported Languages**: Portuguese (pt-BR) and English (en-US)
- **Automatic Translations**: All messages, descriptions and prompts are translated
- **Flexible Configuration**: Via SYNAPSTOR_LANGUAGE or programmatic configuration
- **Fallback System**: English as automatic fallback language
- **Thread-Safe**: Safe system for concurrent applications
- **Interpolation**: Variable support with `{variable}` in translations

### Configuration and Environment Variables
Based on Pydantic Settings with automatic validation:
- **QdrantSettings**: Qdrant database configuration (URL, API key, collection)
- **EmbeddingProviderSettings**: Embedding configuration (provider, model)
- **ToolSettings**: MCP tool description configuration
- **I18nSettings**: Language configuration (SYNAPSTOR_LANGUAGE=pt/en)
- **ServerSettings**: HTTP server configuration (host, port, CORS)

### ID Patterns and Indexing
- Deterministic IDs to avoid document duplication
- Respects .gitignore rules during indexing
- Parallel processing with configurable workers
- Automatic binary file detection

## MCP Integration
Project implements Model Context Protocol for LLM integration:
- **stdio**: For direct LLM integration via stdin/stdout
- **sse**: For Server-Sent Events, useful for web applications
- **http**: For Streamable HTTP MCP, the new standard for HTTP servers
- Basic store/find tools for semantic storage
- **Modo Synapstor**: Advanced multidisciplinary reasoning system with RAG
- Flexible tool description configuration via environment variables
- Host/port configuration for HTTP transport via .env or CLI arguments

## Modo Synapstor - Advanced Functionality
MCP tool that provides structured prompts for multidisciplinary reasoning:
- **Dynamic Instructions**: Guides LLM to generate appropriate experts for each topic
- **Contextual RAG**: Provides relevant documents automatically retrieved from Qdrant
- **Multi-phase Prompts**: Two-phase structure (personality generation + debate)
- **Total Adaptability**: Works for any topic without domain limitations
- **Custom Personalities**: Optional support via JSON for specific cases
- **MCP Architecture**: Synapstor provides context; LLM executes reasoning

## Main Dependencies
- **qdrant-client**: Connectivity with Qdrant vector database
- **fastembed**: Fast embedding generation
- **sentence-transformers**: Alternative embedding models
- **mcp[cli]**: Model Context Protocol implementation
- **fastapi/uvicorn**: Web server for SSE transport
- **pydantic-settings**: Type-based configuration

## Code Conventions
- Uses conventional commits with commitizen
- Formatting with black
- Linting with ruff
- Type checking with mypy (flexible configuration)
- Mandatory pre-commit hooks
- Automatic semantic versioning

---

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
