# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

### Ferramentas CLI
```bash
# Comando principal de controle
synapstor-ctl start
synapstor-ctl start --transport http --host 0.0.0.0 --port 8000
synapstor-ctl indexer --project nome-projeto --path /caminho/projeto
synapstor-ctl stop

# Iniciar servidor MCP com diferentes transportes
synapstor-server --transport stdio    # Para integração direta com LLMs
synapstor-server --transport sse      # Para Server-Sent Events
synapstor-server --transport http     # Para Streamable HTTP MCP
synapstor-server --transport http --host 0.0.0.0 --port 8000

# Indexar projeto
synapstor-indexer --project meu-projeto --path /caminho/do/projeto
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

## Arquitetura do Projeto

### Estrutura Principal
- **src/synapstor/**: Pacote principal do projeto
  - **embeddings/**: Sistema modular de embeddings vetoriais usando FastEmbed e Sentence Transformers
  - **plugins/**: Sistema extensível de plugins com ferramentas como tool_changelog e tool_boilerplate
  - **tools/**: Ferramentas CLI, especialmente indexer.py para indexação em lote
  - **utils/**: Utilitários auxiliares como id_generator para IDs determinísticos
  - **qdrant.py**: Conector principal para banco de dados Qdrant
  - **settings.py**: Configurações baseadas em Pydantic Settings com suporte a variáveis de ambiente
  - **mcp_server.py**: Implementação do servidor MCP (Model Context Protocol)
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

### Configuração e Variáveis de Ambiente
Baseado em Pydantic Settings com validação automática:
- **QdrantSettings**: Configuração do banco Qdrant (URL, API key, coleção)
- **EmbeddingProviderSettings**: Configuração de embeddings (provedor, modelo)
- **ToolSettings**: Configuração de descrições de ferramentas MCP

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