# CLI do Synapstor | Synapstor CLI

## Índice | Table of Contents
- [Português](#português)
- [English](#english)

---

<a name="português"></a>
# Português

Interface de linha de comando para gerenciamento do Synapstor, uma ferramenta para indexação e busca de conteúdo de código.

## Suporte Bilíngue

O Synapstor agora oferece suporte bilíngue completo em inglês e português. Para mais informações sobre como usar as versões em inglês ou português dos scripts, consulte o [Guia Bilíngue](README_BILINGUAL.md).

## Visão Geral

A CLI do Synapstor oferece um conjunto de ferramentas para:

- **Configuração**: Configuração interativa do ambiente
- **Gerenciamento do Servidor**: Iniciar, parar e monitorar o servidor Synapstor
- **Indexação**: Indexar projetos e arquivos no Qdrant
- **Busca**: Buscar conteúdo indexado através do servidor

## Comandos Disponíveis

### `synapstor-ctl`

Gerencia o servidor Synapstor como um serviço:

```bash
synapstor-ctl [comando] [opções]
```

| Comando   | Descrição                                         |
|-----------|---------------------------------------------------|
| `start`   | Inicia o servidor em segundo plano                |
| `stop`    | Para o servidor em execução                       |
| `status`  | Verifica o status do servidor                     |
| `logs`    | Exibe os logs do servidor                         |
| `reindex` | Reindexar um projeto                              |
| `setup`   | Executa a configuração inicial do Synapstor       |
| `indexer` | Executa o indexador do Synapstor                  |

#### Opções do comando `start`

```bash
synapstor-ctl start [--transport {stdio,sse}] [--env-file CAMINHO] [--configure]
```

- `--transport`: Protocolo de transporte (stdio ou sse)
- `--env-file`: Caminho para o arquivo .env
- `--configure`: Configura o ambiente antes de iniciar o servidor

#### Opções do comando `logs`

```bash
synapstor-ctl logs [--follow] [--tail N] [--clear]
```

- `-f, --follow`: Acompanha os logs em tempo real
- `-n, --tail N`: Exibe apenas as últimas N linhas do log
- `--clear`: Limpa o arquivo de log

#### Opções do comando `reindex`

```bash
synapstor-ctl reindex --project NOME [--path CAMINHO] [--env-file CAMINHO] [--force]
```

- `--project`: Nome do projeto a ser indexado (obrigatório)
- `--path`: Caminho do projeto a ser indexado
- `--env-file`: Caminho para o arquivo .env
- `--force`: Força a reindexação mesmo que não haja mudanças

#### Opções do comando `indexer`

```bash
synapstor-ctl indexer --project NOME --path CAMINHO [--collection NOME] [--env-file CAMINHO] [--verbose] [--dry-run]
```

- `--project`: Nome do projeto a ser indexado (obrigatório)
- `--path`: Caminho do projeto a ser indexado (obrigatório)
- `--collection`: Nome da coleção para armazenar (opcional)
- `--env-file`: Caminho para o arquivo .env
- `--verbose`: Exibe informações detalhadas durante a indexação
- `--dry-run`: Simula a indexação sem enviar ao Qdrant

### `synapstor-server`

Inicia o servidor Synapstor:

```bash
synapstor-server [--transport {stdio,sse}] [--env-file CAMINHO] [--create-env] [--configure]
```

- `--transport`: Protocolo de transporte (stdio ou sse, padrão: stdio)
- `--env-file`: Caminho para o arquivo .env (padrão: .env)
- `--create-env`: Cria um arquivo .env de exemplo se não existir
- `--configure`: Configura o ambiente antes de iniciar o servidor

### `synapstor-reindex`

Reindexação de projetos no Qdrant:

```bash
synapstor-reindex --project NOME [--path CAMINHO] [--env-file CAMINHO] [--force]
```

- `--project`: Nome do projeto a ser indexado
- `--path`: Caminho do projeto a ser indexado
- `--env-file`: Caminho para o arquivo .env
- `--force`: Força a reindexação mesmo que não haja mudanças

### `synapstor-setup`

Configura o ambiente Synapstor interativamente:

```bash
synapstor-setup
```

Durante a configuração, você pode optar por instalar scripts de inicialização que facilitam o uso do Synapstor. Você pode escolher onde instalar esses scripts:

1. **Diretório atual**: Instala no diretório onde o comando foi executado
2. **Diretório de usuário**: Instala em `~/.synapstor/bin/` (com opção de adicionar ao PATH em sistemas Unix)
3. **Diretório personalizado**: Você pode especificar qualquer diretório

### `synapstor-indexer`

Interface para o indexador original do Synapstor:

```bash
synapstor-indexer [argumentos]
```

## Configuração

O Synapstor usa um arquivo `.env` para configuração:

### Variáveis Obrigatórias

- `QDRANT_URL`: URL do servidor Qdrant
- `COLLECTION_NAME`: Nome da coleção no Qdrant
- `EMBEDDING_PROVIDER`: Provedor de embeddings
- `EMBEDDING_MODEL`: Modelo de embeddings

### Variáveis Opcionais

- `QDRANT_API_KEY`: Chave API do servidor Qdrant
- `QDRANT_LOCAL_PATH`: Caminho para armazenamento local do Qdrant
- `QDRANT_SEARCH_LIMIT`: Limite de resultados de busca
- `LOG_LEVEL`: Nível de log

## Exemplos de Uso

### Configuração Inicial

```bash
synapstor-setup
```

### Iniciar o Servidor

```bash
synapstor-ctl start
```

Ou, se você criou os scripts de inicialização:

```bash
# Windows
start-synapstor.bat
# Ou PowerShell
./Start-Synapstor.ps1

# Linux/macOS
./start-synapstor.sh
```

### Verificar Status

```bash
synapstor-ctl status
```

### Indexar um Projeto

```bash
synapstor-ctl indexer --project meu-projeto --path /caminho/do/projeto
```

### Reindexar um Projeto

```bash
synapstor-ctl reindex --project meu-projeto --path /caminho/do/projeto
```

### Monitorar Logs

```bash
synapstor-ctl logs --follow
```

### Parar o Servidor

```bash
synapstor-ctl stop
```

## Arquivos de Log e PID

- PID: `~/.synapstor/synapstor.pid`
- Logs: `~/.synapstor/synapstor.log`

## Dependências

- Python 3.8+
- Qdrant Client
- FastEmbed (ou outro provedor de embeddings configurado)
- psutil
- dotenv

---

<a name="english"></a>
# English

Command-line interface for managing Synapstor, a tool for indexing and searching code content.

## Bilingual Support

Synapstor now offers full bilingual support in English and Portuguese. For more information on how to use the English or Portuguese versions of the scripts, see the [Bilingual Guide](README_BILINGUAL.md).

## Overview

The Synapstor CLI offers a suite of tools for:

- **Configuration**: Interactive environment setup
- **Server Management**: Start, stop, and monitor the Synapstor server
- **Indexing**: Index projects and files in Qdrant
- **Search**: Search indexed content through the server

## Available Commands

### `synapstor-ctl`

Manages the Synapstor server as a service:

```bash
synapstor-ctl [command] [options]
```

| Command   | Description                                      |
|-----------|--------------------------------------------------|
| `start`   | Starts the server in the background              |
| `stop`    | Stops the running server                         |
| `status`  | Checks the server status                         |
| `logs`    | Displays server logs                             |
| `reindex` | Reindexes a project                              |
| `setup`   | Runs the initial Synapstor setup                 |
| `indexer` | Runs the Synapstor indexer                       |

#### Options for `start` command

```bash
synapstor-ctl start [--transport {stdio,sse}] [--env-file PATH] [--configure]
```

- `--transport`: Transport protocol (stdio or sse)
- `--env-file`: Path to the .env file
- `--configure`: Configures the environment before starting the server

#### Options for `logs` command

```bash
synapstor-ctl logs [--follow] [--tail N] [--clear]
```

- `-f, --follow`: Follows logs in real-time
- `-n, --tail N`: Displays only the last N lines of the log
- `--clear`: Clears the log file

#### Options for `reindex` command

```bash
synapstor-ctl reindex --project NAME [--path PATH] [--env-file PATH] [--force]
```

- `--project`: Name of the project to be indexed (required)
- `--path`: Path to the project to be indexed
- `--env-file`: Path to the .env file
- `--force`: Forces reindexing even if there are no changes

#### Options for `indexer` command

```bash
synapstor-ctl indexer --project NAME --path PATH [--collection NAME] [--env-file PATH] [--verbose] [--dry-run]
```

- `--project`: Name of the project to be indexed (required)
- `--path`: Path to the project to be indexed (required)
- `--collection`: Name of the collection to store in (optional)
- `--env-file`: Path to the .env file
- `--verbose`: Displays detailed information during indexing
- `--dry-run`: Simulates indexing without sending to Qdrant

### `synapstor-server`

Starts the Synapstor server:

```bash
synapstor-server [--transport {stdio,sse}] [--env-file PATH] [--create-env] [--configure]
```

- `--transport`: Transport protocol (stdio or sse, default: stdio)
- `--env-file`: Path to the .env file (default: .env)
- `--create-env`: Creates an example .env file if it doesn't exist
- `--configure`: Configures the environment before starting the server

### `synapstor-reindex`

Reindexing projects in Qdrant:

```bash
synapstor-reindex --project NAME [--path PATH] [--env-file PATH] [--force]
```

- `--project`: Name of the project to be indexed
- `--path`: Path to the project to be indexed
- `--env-file`: Path to the .env file
- `--force`: Forces reindexing even if there are no changes

### `synapstor-setup`

Configures the Synapstor environment interactively:

```bash
synapstor-setup
```

During setup, you can choose to install startup scripts that facilitate using Synapstor. You can choose where to install these scripts:

1. **Current directory**: Installs in the directory where the command was executed
2. **User directory**: Installs in `~/.synapstor/bin/` (with option to add to PATH on Unix systems)
3. **Custom directory**: You can specify any directory

### `synapstor-indexer`

Interface for the original Synapstor indexer:

```bash
synapstor-indexer [arguments]
```

## Configuration

Synapstor uses a `.env` file for configuration:

### Required Variables

- `QDRANT_URL`: URL of the Qdrant server
- `COLLECTION_NAME`: Name of the collection in Qdrant
- `EMBEDDING_PROVIDER`: Embeddings provider
- `EMBEDDING_MODEL`: Embeddings model

### Optional Variables

- `QDRANT_API_KEY`: API key for the Qdrant server
- `QDRANT_LOCAL_PATH`: Path for local Qdrant storage
- `QDRANT_SEARCH_LIMIT`: Search results limit
- `LOG_LEVEL`: Log level

## Usage Examples

### Initial Configuration

```bash
synapstor-setup
```

### Start the Server

```bash
synapstor-ctl start
```

Or, if you created the startup scripts:

```bash
# Windows
start-synapstor.bat
# Or PowerShell
./Start-Synapstor.ps1

# Linux/macOS
./start-synapstor.sh
```

### Check Status

```bash
synapstor-ctl status
```

### Index a Project

```bash
synapstor-ctl indexer --project my-project --path /path/to/project
```

### Reindex a Project

```bash
synapstor-ctl reindex --project my-project --path /path/to/project
```

### Monitor Logs

```bash
synapstor-ctl logs --follow
```

### Stop the Server

```bash
synapstor-ctl stop
```

## Log and PID Files

- PID: `~/.synapstor/synapstor.pid`
- Logs: `~/.synapstor/synapstor.log`

## Dependencies

- Python 3.8+
- Qdrant Client
- FastEmbed (or another configured embeddings provider)
- psutil
- dotenv
