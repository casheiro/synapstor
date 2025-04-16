# CLI do Synapstor

Interface de linha de comando para gerenciamento do Synapstor, uma ferramenta para indexação e busca de conteúdo de código.

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