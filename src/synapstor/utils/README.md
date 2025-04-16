# Utilitários do Synapstor

Este módulo contém funções utilitárias comuns utilizadas em diferentes partes do Synapstor.

## Visão Geral

O módulo `utils` fornece um conjunto de funções auxiliares e utilitários que podem ser usados por diversos componentes do sistema. Estas ferramentas são projetadas para resolver problemas específicos e recorrentes de forma consistente.

## Funcionalidades

### Gerador de IDs Determinísticos (`id_generator.py`)

Este utilitário fornece funções para geração de identificadores únicos e determinísticos, essenciais para o armazenamento e atualização de documentos no Qdrant sem criar duplicações.

#### Funções Disponíveis

##### `gerar_id_determinista(metadata: Dict[str, Any]) -> str`

Gera um ID único e determinístico baseado nos metadados de um documento.

```python
from synapstor.utils import gerar_id_determinista

metadados = {
    "projeto": "meu-projeto",
    "caminho_absoluto": "/caminho/completo/arquivo.py",
    "nome_arquivo": "arquivo.py"
}

# Gera um ID único baseado nos metadados
id_documento = gerar_id_determinista(metadados)
print(id_documento)  # Ex: "a1b2c3d4e5f6g7h8i9j0"
```

**Parâmetros:**
- `metadata`: Dicionário de metadados que deve conter pelo menos:
  - `projeto`: Nome do projeto
  - `caminho_absoluto`: Caminho completo do arquivo
  - Ou outras informações únicas que possam identificar o documento

**Retorno:**
- String hexadecimal MD5 que representa um ID único e consistente

**Comportamento:**
- Se o mesmo dicionário de metadados for passado várias vezes, sempre gerará o mesmo ID
- Prioriza `projeto` e `caminho_absoluto` como identificadores principais
- Fallback para outros metadados quando os identificadores principais não estão disponíveis
- Lança `ValueError` se não houver metadados suficientes para gerar um ID

##### `extrair_id_numerico(id_hex: str, digitos: int = 8) -> int`

Converte um ID hexadecimal em um valor inteiro.

```python
from synapstor.utils import extrair_id_numerico

# Converte um hash hexadecimal para um número inteiro
id_hex = "a1b2c3d4e5f6g7h8i9j0"
id_numerico = extrair_id_numerico(id_hex)
print(id_numerico)  # Ex: 2712418772
```

**Parâmetros:**
- `id_hex`: Hash hexadecimal a ser convertido
- `digitos`: Número de caracteres hexadecimais a usar (padrão: 8)

**Retorno:**
- Valor inteiro extraído do hash

## Uso no Sistema

### Aplicação no Indexador

O gerador de IDs determinísticos é utilizado pelo indexador (`tools/indexer.py`) para garantir que:

1. O mesmo arquivo nunca seja indexado duas vezes (evitando duplicações)
2. Atualizações no conteúdo de um arquivo substituam a versão anterior
3. A reindexação completa de um projeto não crie entradas duplicadas

```python
# Exemplo de uso no indexador
metadata = {
    "projeto": nome_projeto,
    "caminho_absoluto": str(caminho_arquivo),
    "nome_arquivo": caminho_arquivo.name,
    "extensao": caminho_arquivo.suffix[1:] if caminho_arquivo.suffix else "",
}

# Gera um ID que sempre será o mesmo para o mesmo arquivo
documento_id = gerar_id_determinista(metadata)

# Atualiza ou cria o documento no Qdrant
qdrant_client.upsert(
    collection_name=collection_name,
    points=[
        models.PointStruct(
            id=documento_id,  # Usa o ID determinístico
            payload={"metadata": metadata, "document": conteudo},
            vector=embedding
        )
    ]
)
```

## Benefícios

- **Consistência**: Garante que entidades únicas tenham IDs únicos
- **Idempotência**: Permite operações repetidas sem efeitos colaterais (reindexações)
- **Rastreabilidade**: Facilita o acompanhamento de documentos entre diferentes processos 