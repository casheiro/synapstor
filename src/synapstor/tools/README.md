# Ferramentas do Synapstor

## 🌎 Idioma / Language

- [Português 🇧🇷](#português)
- [English 🇺🇸](#english)

---

<a name="português"></a>
# Português 🇧🇷

Este módulo contém ferramentas utilitárias para o Synapstor, incluindo o poderoso indexador semântico que facilita o armazenamento e recuperação de conteúdo no Qdrant.

## Indexador (`indexer.py`)

O Indexador é uma ferramenta robusta para processar e indexar projetos inteiros no Qdrant, permitindo buscas semânticas eficientes sobre o código fonte e documentação.

### Visão Geral

O Indexador foi projetado para:

- **Processamento em Lote**: Indexar projetos completos de uma só vez
- **Independência**: Funcionar sem depender do servidor MCP
- **Paralelismo**: Processar múltiplos arquivos simultaneamente
- **Integração .gitignore**: Respeitar as regras de exclusão já definidas no projeto
- **IDs Determinísticos**: Evitar duplicidades nos documentos indexados

### Funcionalidades Principais

- **Detecção Automática de Binários**: Ignora automaticamente arquivos binários
- **Filtragem Inteligente**: Utiliza as regras do .gitignore para evitar indexar arquivos desnecessários
- **Configuração Flexível**: Suporta configuração via argumentos ou arquivo .env
- **Feedback Visual**: Exibe barras de progresso e estatísticas durante o processamento
- **Resiliência**: Tratamento de erros e limites de tamanho de arquivo

### Uso via Linha de Comando

```bash
python -m synapstor.tools.indexer --project <nome_projeto> --path <caminho_projeto> [opções]
```

#### Argumentos Obrigatórios

- `--project, -p`: Nome do projeto (usado como metadado para filtragem)
- `--path, -d`: Caminho para o diretório do projeto a ser indexado

#### Argumentos Opcionais

- `--collection, -c`: Nome da coleção no Qdrant (padrão: "synapstor")
- `--qdrant-url`: URL do servidor Qdrant (alternativa: variável de ambiente QDRANT_URL)
- `--qdrant-api-key`: Chave API do Qdrant (alternativa: variável de ambiente QDRANT_API_KEY)
- `--embedding-model`: Modelo de embeddings a ser usado (padrão: "sentence-transformers/all-MiniLM-L6-v2")
- `--vector-name`: Nome personalizado para o vetor no Qdrant
- `--workers, -w`: Número de workers paralelos (padrão: 4)
- `--max-file-size`: Tamanho máximo de arquivo em MB (padrão: 5)
- `--verbose, -v`: Modo detalhado com mais informações
- `--recreate-collection`: Recria a coleção caso ela já exista
- `--query, -q`: Realiza uma busca após concluir a indexação

### Exemplo de Uso Básico

```bash
# Indexar um projeto Python
python -m synapstor.tools.indexer --project meu-projeto --path /caminho/para/meu-projeto

# Indexar com configurações personalizadas
python -m synapstor.tools.indexer \
    --project meu-projeto \
    --path /caminho/para/meu-projeto \
    --collection colecao-personalizada \
    --workers 8 \
    --verbose
```

### Através da CLI do Synapstor

```bash
# Usando o synapstor-indexer
synapstor-indexer --project meu-projeto --path /caminho/para/meu-projeto

# Usando synapstor-ctl
synapstor-ctl indexer --project meu-projeto --path /caminho/para/meu-projeto
```

### Uso Programático

O Indexador também pode ser usado diretamente no código:

```python
from synapstor.tools.indexer import IndexadorDireto

# Inicializa o indexador
indexador = IndexadorDireto(
    nome_projeto="meu-projeto",
    caminho_projeto="/caminho/do/projeto",
    collection_name="minha-colecao",
    max_workers=4
)

# Executa a indexação
indexador.indexar()

# Realiza buscas na coleção
resultados = indexador.buscar("Como implementar autenticação?", limite=5)
for res in resultados:
    print(f"Score: {res['score']}")
    print(f"Arquivo: {res['metadata']['nome_arquivo']}")
    print(f"Trecho: {res['documento'][:200]}...")
    print("-" * 50)
```

### Configuração via .env

O Indexador pode ser configurado através de um arquivo .env com as seguintes variáveis:

```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=sua-chave-api
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
COLLECTION_NAME=synapstor
```

### Metadados Armazenados

Cada documento indexado contém os seguintes metadados:

| Campo | Descrição |
|-------|-----------|
| `projeto` | Nome do projeto |
| `caminho_absoluto` | Caminho absoluto do arquivo |
| `caminho_relativo` | Caminho relativo à raiz do projeto |
| `nome_arquivo` | Nome do arquivo com extensão |
| `extensao` | Extensão do arquivo (sem ponto) |
| `tamanho_bytes` | Tamanho do arquivo em bytes |
| `data_modificacao` | Data da última modificação |

### Detalhes Técnicos

#### Geração de Embeddings

O indexador usa a biblioteca `sentence-transformers` para gerar vetores de embeddings. Por padrão, utiliza o modelo "all-MiniLM-L6-v2", que oferece um bom equilíbrio entre qualidade e desempenho.

#### IDs Determinísticos

Para evitar duplicações, o indexador gera IDs determinísticos baseados no nome do projeto e caminho absoluto do arquivo. Isso permite reindexar o mesmo projeto múltiplas vezes sem criar documentos duplicados.

#### Filtragem de Arquivos

O indexador aplica as seguintes regras de filtragem:

1. Ignora arquivos listados no `.gitignore`
2. Pula arquivos com extensões binárias conhecidas (imagens, executáveis, etc.)
3. Ignora arquivos maiores que o tamanho máximo configurado
4. Pula arquivos que não podem ser decodificados como texto

## Dependências

- `qdrant-client`: Cliente Python oficial para o Qdrant
- `sentence-transformers`: Biblioteca para geração de embeddings
- `pathspec`: Para processamento de regras no estilo .gitignore
- `tqdm`: Para barras de progresso interativas

---

<a name="english"></a>
# English 🇺🇸

This module contains utility tools for Synapstor, including the powerful semantic indexer that facilitates the storage and retrieval of content in Qdrant.

## Indexer (`indexer.py`)

The Indexer is a robust tool for processing and indexing entire projects in Qdrant, enabling efficient semantic searches across source code and documentation.

### Overview

The Indexer was designed for:

- **Batch Processing**: Index complete projects in a single operation
- **Independence**: Function without depending on the MCP server
- **Parallelism**: Process multiple files simultaneously
- **Integration with .gitignore**: Respect exclusion rules already defined in the project
- **Deterministic IDs**: Avoid duplications in indexed documents

### Main Features

- **Automatic Binary Detection**: Automatically ignores binary files
- **Intelligent Filtering**: Uses .gitignore rules to avoid indexing unnecessary files
- **Flexible Configuration**: Supports configuration via arguments or .env file
- **Visual Feedback**: Displays progress bars and statistics during processing
- **Resilience**: Error handling and file size limits

### Command Line Usage

```bash
python -m synapstor.tools.indexer --project <project_name> --path <project_path> [options]
```

#### Required Arguments

- `--project, -p`: Project name (used as metadata for filtering)
- `--path, -d`: Path to the project directory to be indexed

#### Optional Arguments

- `--collection, -c`: Collection name in Qdrant (default: "synapstor")
- `--qdrant-url`: Qdrant server URL (alternative: QDRANT_URL environment variable)
- `--qdrant-api-key`: Qdrant API key (alternative: QDRANT_API_KEY environment variable)
- `--embedding-model`: Embedding model to use (default: "sentence-transformers/all-MiniLM-L6-v2")
- `--vector-name`: Custom name for the vector in Qdrant
- `--workers, -w`: Number of parallel workers (default: 4)
- `--max-file-size`: Maximum file size in MB (default: 5)
- `--verbose, -v`: Detailed mode with more information
- `--recreate-collection`: Recreates the collection if it already exists
- `--query, -q`: Performs a search after completing indexing

### Basic Usage Example

```bash
# Index a Python project
python -m synapstor.tools.indexer --project my-project --path /path/to/my-project

# Index with custom settings
python -m synapstor.tools.indexer \
    --project my-project \
    --path /path/to/my-project \
    --collection custom-collection \
    --workers 8 \
    --verbose
```

### Through Synapstor CLI

```bash
# Using synapstor-indexer
synapstor-indexer --project my-project --path /path/to/my-project

# Using synapstor-ctl
synapstor-ctl indexer --project my-project --path /path/to/my-project
```

### Programmatic Usage

The Indexer can also be used directly in code:

```python
from synapstor.tools.indexer import DirectIndexer

# Initialize the indexer
indexer = DirectIndexer(
    project_name="my-project",
    project_path="/path/to/project",
    collection_name="my-collection",
    max_workers=4
)

# Run indexing
indexer.index()

# Perform searches in the collection
results = indexer.search("How to implement authentication?", limit=5)
for res in results:
    print(f"Score: {res['score']}")
    print(f"File: {res['metadata']['file_name']}")
    print(f"Excerpt: {res['document'][:200]}...")
    print("-" * 50)
```

### Configuration via .env

The Indexer can be configured through a .env file with the following variables:

```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-api-key
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
COLLECTION_NAME=synapstor
```

### Stored Metadata

Each indexed document contains the following metadata:

| Field | Description |
|-------|-------------|
| `project` | Project name |
| `absolute_path` | Absolute path of the file |
| `relative_path` | Path relative to project root |
| `file_name` | File name with extension |
| `extension` | File extension (without dot) |
| `size_bytes` | File size in bytes |
| `modification_date` | Last modification date |

### Technical Details

#### Embedding Generation

The indexer uses the `sentence-transformers` library to generate embedding vectors. By default, it uses the "all-MiniLM-L6-v2" model, which offers a good balance between quality and performance.

#### Deterministic IDs

To avoid duplications, the indexer generates deterministic IDs based on the project name and absolute file path. This allows reindexing the same project multiple times without creating duplicate documents.

#### File Filtering

The indexer applies the following filtering rules:

1. Ignores files listed in `.gitignore`
2. Skips files with known binary extensions (images, executables, etc.)
3. Ignores files larger than the configured maximum size
4. Skips files that cannot be decoded as text

## Dependencies

- `qdrant-client`: Official Python client for Qdrant
- `sentence-transformers`: Library for generating embeddings
- `pathspec`: For processing .gitignore-style rules
- `tqdm`: For interactive progress bars
