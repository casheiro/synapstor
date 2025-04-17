# Ferramentas do Synapstor

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
