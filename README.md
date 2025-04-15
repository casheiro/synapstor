# Synapstor: Um servidor MCP para Qdrant com memória semântica

[![smithery badge](https://smithery.ai/badge/mcp-server-qdrant)](https://smithery.ai/protocol/mcp-server-qdrant)

> Synapstor é uma evolução não oficial do [mcp-server-qdrant](https://github.com/modelcontextprotocol/mcp-server-qdrant), trazendo uma interface de linha de comando aprimorada e facilidades de instalação e configuração.

## Visão Geral

O [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) é um protocolo aberto que possibilita a integração perfeita entre aplicações de LLM e fontes externas de dados e ferramentas. O Synapstor implementa este protocolo para fornecer uma camada de memória semântica sobre o banco de dados vetorial [Qdrant](https://qdrant.tech/).

Com o Synapstor, você pode:
- Armazenar informações com metadados no Qdrant
- Recuperar informações relevantes usando busca semântica
- Integrar com várias ferramentas de IA como Claude, Cursor e outras

<a href="https://glama.ai/mcp/servers/9ejy5scw5i"><img width="380" height="200" src="https://glama.ai/mcp/servers/9ejy5scw5i/badge" alt="mcp-server-qdrant MCP server" /></a>

## Componentes

### Ferramentas

1. `qdrant-store`
   - Armazena informações no banco de dados Qdrant
   - Entrada:
     - `information` (string): Informação a ser armazenada
     - `metadata` (JSON): Metadados opcionais para armazenar
     - `collection_name` (string): Nome da coleção onde armazenar a informação (opcional se houver uma coleção padrão configurada)
   - Retorna: Mensagem de confirmação

2. `qdrant-find`
   - Recupera informações relevantes do banco de dados Qdrant
   - Entrada:
     - `query` (string): Consulta para a busca
     - `collection_name` (string): Nome da coleção onde buscar (opcional se houver uma coleção padrão configurada)
   - Retorna: Informações armazenadas no Qdrant como mensagens separadas

## Instalação

### Instalação Rápida

1. **Instalar a partir do código fonte**:

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/synapstor.git
cd synapstor

# Instalar o pacote em modo de desenvolvimento
pip install -e .
```

2. **Executar o script de configuração**:

```bash
# Configuração interativa
synapstor-setup
```

O script de configuração irá:
- Verificar e instalar dependências necessárias
- Guiá-lo pela configuração das conexões do Qdrant
- Criar scripts de inicialização para sua plataforma
- Gerar um arquivo .env com suas configurações

### Comandos CLI

O Synapstor fornece várias ferramentas de linha de comando:

| Comando | Descrição |
|---------|-----------|
| `synapstor-setup` | Configuração e instalação interativa |
| `synapstor-config` | Atualizar configurações |
| `synapstor-server` | Iniciar o servidor MCP |
| `synapstor-indexer` | Indexar conteúdo no Qdrant |

### Iniciar o Servidor

Após a instalação, você pode iniciar o servidor de várias maneiras:

```bash
# Uso básico
synapstor-server

# Com protocolo de transporte específico
synapstor-server --transport sse

# Criar arquivo .env se não existir
synapstor-server --create-env

# Configurar antes de iniciar
synapstor-server --configure

# Usar arquivo .env personalizado
synapstor-server --env-file personalizado.env
```

### Indexação de Conteúdo

O Synapstor inclui um indexador poderoso para adicionar conteúdo à sua coleção Qdrant:

```bash
# Indexação básica de um projeto
synapstor-indexer --project meu-projeto --path /caminho/do/projeto

# Opções adicionais
synapstor-indexer --project meu-projeto --path /caminho/do/projeto \
  --collection minha-colecao \
  --workers 8 \
  --verbose
```

## Configuração

### Usando Variáveis de Ambiente

A configuração do servidor pode ser feita usando variáveis de ambiente como listado abaixo.

### Usando Arquivo .env (Recomendado)

O servidor suporta configuração via arquivo `.env` no diretório raiz do projeto. Esta é a forma recomendada para configurar o servidor para desenvolvimento e uso local.

1. Crie um arquivo `.env` no diretório raiz do projeto (automaticamente criado com `synapstor-setup` ou `synapstor-server --create-env`)
2. Defina as variáveis de ambiente necessárias no arquivo
3. Execute o servidor - ele carregará automaticamente a configuração do arquivo `.env`

Se nenhum arquivo `.env` for encontrado, o servidor procurará variáveis de ambiente no sistema. Se variáveis obrigatórias estiverem faltando, ele solicitará que você crie um arquivo `.env`.

### Variáveis de Ambiente Obrigatórias

| Nome | Descrição | Valor Padrão |
|------|-----------|--------------|
| `QDRANT_URL` | URL do servidor Qdrant | Nenhum |
| `QDRANT_API_KEY` | Chave API para o servidor Qdrant | Nenhum |
| `COLLECTION_NAME` | Nome da coleção padrão a ser usada | Nenhum |

### Variáveis de Ambiente Opcionais

| Nome | Descrição | Valor Padrão |
|------|-----------|--------------|
| `QDRANT_LOCAL_PATH` | Caminho para o banco de dados Qdrant local (alternativa ao `QDRANT_URL`) | Nenhum |
| `EMBEDDING_PROVIDER` | Provedor de embeddings a ser usado (atualmente apenas "fastembed" é suportado) | `fastembed` |
| `EMBEDDING_MODEL` | Nome do modelo de embedding a ser usado | `sentence-transformers/all-MiniLM-L6-v2` |
| `TOOL_STORE_DESCRIPTION` | Descrição personalizada para a ferramenta store | Ver padrão em [`settings.py`](src/synapstor/settings.py) |
| `TOOL_FIND_DESCRIPTION` | Descrição personalizada para a ferramenta find | Ver padrão em [`settings.py`](src/synapstor/settings.py) |
| `LOG_LEVEL` | Nível de log (DEBUG, INFO, WARNING, ERROR) | INFO |

Nota: Você não pode fornecer `QDRANT_URL` e `QDRANT_LOCAL_PATH` ao mesmo tempo.

> [!IMPORTANTE]
> Embora variáveis de ambiente sejam suportadas, recomenda-se usar os comandos `synapstor-setup` ou `synapstor-config` para uma configuração mais fácil.

## Uso com Diferentes Clientes

### Usando com Docker

Um Dockerfile está disponível para construir e executar o servidor MCP:

```bash
# Construir o container
docker build -t synapstor .

# Executar o container
docker run -p 8000:8000 \
  -e QDRANT_URL="http://seu-servidor-qdrant:6333" \
  -e QDRANT_API_KEY="sua-chave-api" \
  -e COLLECTION_NAME="sua-colecao" \
  synapstor
```

### Configuração manual para Claude Desktop

Para usar este servidor com o aplicativo Claude Desktop, adicione a seguinte configuração à seção "mcpServers" do seu arquivo `claude_desktop_config.json`:

```json
{
  "qdrant": {
    "command": "synapstor-server",
    "args": ["--transport", "stdio"],
    "env": {
      "QDRANT_URL": "https://xyz-exemplo.eu-central.aws.cloud.qdrant.io:6333",
      "QDRANT_API_KEY": "sua_chave_api",
      "COLLECTION_NAME": "nome-da-sua-colecao",
      "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
    }
  }
}
```

Para modo Qdrant local:

```json
{
  "qdrant": {
    "command": "synapstor-server",
    "args": ["--transport", "stdio"],
    "env": {
      "QDRANT_LOCAL_PATH": "/caminho/para/banco/qdrant",
      "COLLECTION_NAME": "nome-da-sua-colecao",
      "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
    }
  }
}
```

Este servidor MCP criará automaticamente uma coleção com o nome especificado se ela não existir.

Por padrão, o servidor usará o modelo de embedding `sentence-transformers/all-MiniLM-L6-v2` para codificar memórias.
Por enquanto, apenas modelos [FastEmbed](https://qdrant.github.io/fastembed/) são suportados.

## Suporte para outras ferramentas

Este servidor MCP pode ser usado com qualquer cliente compatível com MCP. Por exemplo, você pode usá-lo com [Cursor](https://docs.cursor.com/context/model-context-protocol), que fornece suporte integrado para o Model Context Protocol.

### Uso com Cursor/Windsurf

Você pode configurar este servidor MCP para funcionar como uma ferramenta de busca de código para Cursor ou Windsurf personalizando as descrições das ferramentas:

```bash
synapstor-server --configure
```

Em seguida, defina os seguintes valores quando solicitado:

- `COLLECTION_NAME`: "code-snippets"
- `TOOL_STORE_DESCRIPTION`: "Armazene trechos de código reutilizáveis para recuperação posterior. O parâmetro 'information' deve conter uma descrição em linguagem natural do que o código faz, enquanto o código real deve ser incluído no parâmetro 'metadata' como uma propriedade 'code'. O valor de 'metadata' é um dicionário Python com strings como chaves. Use isso sempre que gerar algum trecho de código."
- `TOOL_FIND_DESCRIPTION`: "Pesquise trechos de código relevantes com base em descrições em linguagem natural. O parâmetro 'query' deve descrever o que você está procurando, e a ferramenta retornará os trechos de código mais relevantes. Use isso quando precisar encontrar trechos de código existentes para reutilização ou referência."

Após a configuração, inicie o servidor com transporte SSE:

```bash
synapstor-server --transport sse
```

No Cursor/Windsurf, você pode configurar o servidor MCP em suas configurações apontando para este servidor em execução usando o protocolo de transporte SSE. A descrição sobre como adicionar um servidor MCP ao Cursor pode ser encontrada na [documentação do Cursor](https://docs.cursor.com/context/model-context-protocol#adding-an-mcp-server-to-cursor). Se você estiver executando o Cursor/Windsurf localmente, pode usar a seguinte URL:

```
http://localhost:8000/sse
```

> [!DICA]
> Sugerimos o transporte SSE como forma preferida de conectar o Cursor/Windsurf ao servidor MCP, pois ele pode suportar conexões remotas. Isso facilita o compartilhamento do servidor com sua equipe ou o uso em um ambiente de nuvem.

Esta configuração transforma o servidor Synapstor em uma ferramenta especializada de busca de código que pode:

1. Armazenar trechos de código, documentação e detalhes de implementação
2. Recuperar exemplos de código relevantes com base em busca semântica
3. Ajudar desenvolvedores a encontrar implementações específicas ou padrões de uso

Você pode popular o banco de dados armazenando descrições em linguagem natural de trechos de código (no parâmetro `information`) junto com o código real (na propriedade `metadata.code`), e depois pesquisar por eles usando consultas em linguagem natural que descrevem o que você está procurando.

> [!NOTA]
> As descrições de ferramentas fornecidas acima são exemplos e podem precisar ser personalizadas para seu caso de uso específico. Considere ajustar as descrições para melhor corresponder ao fluxo de trabalho da sua equipe e aos tipos específicos de trechos de código que você deseja armazenar e recuperar.

**Se você instalou com sucesso o Synapstor, mas ainda não consegue fazê-lo funcionar com o Cursor, considere criar [regras do Cursor](https://docs.cursor.com/context/rules-for-ai) para que as ferramentas MCP sejam sempre usadas quando o agente produzir um novo trecho de código.** Você pode restringir as regras para funcionarem apenas para certos tipos de arquivo, para evitar usar o servidor MCP para documentação ou outros tipos de conteúdo.

## Adicionando Ferramentas Personalizadas (Sistema de Plugins)

O Synapstor inclui um sistema de plugins que permite adicionar novas ferramentas ao servidor MCP sem modificar o código principal. Isso torna o servidor mais extensível e facilita a adição de funcionalidades personalizadas.

### Como Adicionar Uma Nova Ferramenta

1. Crie um arquivo Python no diretório `src/synapstor/plugins/` com o prefixo `tool_` (exemplo: `tool_calculadora.py`).

2. Implemente sua ferramenta seguindo este modelo:

```python
import logging
from typing import List
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)

async def minha_ferramenta(ctx: Context, parametro1: str) -> str:
    """
    Descrição detalhada da ferramenta.
    
    :param ctx: O contexto da solicitação MCP.
    :param parametro1: Descrição do parâmetro.
    :return: Resultado da operação.
    """
    await ctx.debug(f"Processando: {parametro1}")
    resultado = f"Processado {parametro1}"
    return resultado

def setup_tools(server) -> List[str]:
    """
    Registra as ferramentas deste plugin no servidor.
    """
    server.add_tool(
        minha_ferramenta,
        name="minha-ferramenta",
        description="Descrição da ferramenta."
    )
    return ["minha-ferramenta"]
```

3. O sistema carregará automaticamente sua ferramenta na próxima inicialização do servidor.

### Diretrizes para Desenvolver Ferramentas

- Use funções assíncronas (`async def`) com o primeiro parâmetro sendo `ctx: Context`
- Forneça tipos para todos os parâmetros para melhorar a experiência do cliente
- Inclua documentação detalhada sobre o que a ferramenta faz e seus parâmetros
- Implemente uma função `setup_tools(server)` que registre todas as ferramentas fornecidas

Para obter informações mais detalhadas sobre como desenvolver plugins, consulte o arquivo `src/synapstor/plugins/README.md` no código-fonte.

### Uso com Claude Code

Você pode aprimorar as capacidades do Claude Code conectando-o a este servidor MCP, habilitando a busca semântica em sua base de código existente.

#### Configurando o Synapstor

1. Adicione o servidor MCP ao Claude Code:

    ```shell
    # Adicione o Synapstor configurado para busca de código
    claude mcp add busca-codigo \
    -e QDRANT_URL="http://localhost:6333" \
    -e COLLECTION_NAME="repositorio-codigo" \
    -e EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \
    -e TOOL_STORE_DESCRIPTION="Armazene trechos de código com descrições. O parâmetro 'information' deve conter uma descrição em linguagem natural do que o código faz, enquanto o código real deve ser incluído no parâmetro 'metadata' como uma propriedade 'code'." \
    -e TOOL_FIND_DESCRIPTION="Pesquise trechos de código relevantes usando linguagem natural. O parâmetro 'query' deve descrever a funcionalidade que você está procurando." \
    -- synapstor-server
    ```

2. Verifique se o servidor foi adicionado:

    ```shell
    claude mcp list
    ```

#### Usando a Busca Semântica de Código no Claude Code

As descrições das ferramentas, especificadas em `TOOL_STORE_DESCRIPTION` e `TOOL_FIND_DESCRIPTION`, orientam o Claude Code sobre como usar o servidor MCP. As fornecidas acima são exemplos e podem precisar ser personalizadas para seu caso de uso específico. No entanto, o Claude Code já deve ser capaz de:

1. Usar a ferramenta `qdrant-store` para armazenar trechos de código com descrições.
2. Usar a ferramenta `qdrant-find` para pesquisar trechos de código relevantes usando linguagem natural.

### Executar o servidor MCP em Modo de Desenvolvimento

O servidor MCP pode ser executado em modo de desenvolvimento usando o comando `mcp dev`. Isso iniciará o servidor e abrirá o inspetor MCP em seu navegador.

```shell
COLLECTION_NAME=mcp-dev mcp dev src/synapstor/server.py
```

## Contribuindo

Se você tiver sugestões para melhorar o Synapstor ou quiser relatar um bug, abra uma issue!
Adoraríamos qualquer contribuição.

### Testando o `Synapstor` localmente

O [MCP inspector](https://github.com/modelcontextprotocol/inspector) é uma ferramenta de desenvolvedor para testar e depurar servidores MCP. Ele executa tanto uma UI cliente (porta padrão 5173) quanto um servidor proxy MCP (porta padrão 3000). Abra a UI cliente em seu navegador para usar o inspetor.

```shell
QDRANT_URL=":memory:" COLLECTION_NAME="teste" \
mcp dev src/synapstor/server.py
```

Uma vez iniciado, abra seu navegador em http://localhost:5173 para acessar a interface do inspetor.

## Licença

Este servidor MCP é licenciado sob a Licença Apache 2.0. Isso significa que você é livre para usar, modificar e distribuir o software, sujeito aos termos e condições da Licença Apache 2.0. Para mais detalhes, consulte o arquivo LICENSE no repositório do projeto.

## Perguntas Frequentes (FAQ)

### Sobre o Synapstor

#### O que é o Synapstor?
O Synapstor é uma evolução não oficial do mcp-server-qdrant que implementa o Model Context Protocol (MCP) para fornecer uma camada de memória semântica sobre o banco de dados vetorial Qdrant. Ele permite armazenar, recuperar e buscar informações usando busca semântica, integrando-se perfeitamente com várias ferramentas de IA como Claude, Cursor e outras.

#### Quais são os principais componentes do Synapstor?
O Synapstor oferece duas ferramentas principais:
1. `qdrant-store`: Armazena informações com metadados no banco de dados Qdrant
2. `qdrant-find`: Recupera informações relevantes usando busca semântica

Além disso, inclui várias ferramentas de linha de comando: synapstor-setup, synapstor-config, synapstor-server e synapstor-indexer.

#### Como o Synapstor se diferencia do mcp-server-qdrant original?
O Synapstor aprimora o mcp-server-qdrant original com:
- Interface de linha de comando melhorada
- Facilidades de instalação e configuração
- Ferramentas de indexação mais robustas
- Suporte a metadados mais completo
- Configuração simplificada através de arquivos .env

### Instalação e Configuração

#### Como instalar o Synapstor?
Para instalar o Synapstor:
1. Clone o repositório: `git clone https://github.com/seu-usuario/synapstor.git`
2. Entre no diretório: `cd synapstor`
3. Instale o pacote em modo de desenvolvimento: `pip install -e .`
4. Execute o script de configuração: `synapstor-setup`

#### Quais são as variáveis de ambiente necessárias para configurar o Synapstor?
Variáveis obrigatórias:
- `QDRANT_URL`: URL do servidor Qdrant
- `QDRANT_API_KEY`: Chave API para o servidor Qdrant
- `COLLECTION_NAME`: Nome da coleção padrão a ser usada

Variáveis opcionais:
- `QDRANT_LOCAL_PATH`: Caminho para banco de dados Qdrant local (alternativa ao QDRANT_URL)
- `EMBEDDING_PROVIDER`: Provedor de embeddings (atualmente apenas "fastembed")
- `EMBEDDING_MODEL`: Nome do modelo de embedding
- `TOOL_STORE_DESCRIPTION`: Descrição personalizada para a ferramenta store
- `TOOL_FIND_DESCRIPTION`: Descrição personalizada para a ferramenta find
- `LOG_LEVEL`: Nível de log (DEBUG, INFO, WARNING, ERROR)

#### Como configurar o Synapstor para usar Qdrant local em vez do Qdrant Cloud?
Em vez de configurar `QDRANT_URL` e `QDRANT_API_KEY`, configure `QDRANT_LOCAL_PATH` com o caminho para o diretório onde deseja armazenar os dados localmente. Se usar o comando `synapstor-setup`, você será guiado através das opções, incluindo a escolha entre Qdrant Cloud e local.

### Uso e Funcionalidades

#### Como iniciar o servidor Synapstor?
Após a instalação e configuração, você pode iniciar o servidor com:
```bash
synapstor-server
```

Para iniciar com transporte SSE (recomendado para Cursor):
```bash
synapstor-server --transport sse
```

#### Como indexar um projeto com o Synapstor?
Para indexar um projeto:
```bash
synapstor-indexer --project meu-projeto --path /caminho/do/projeto
```

Opções adicionais:
```bash
synapstor-indexer --project meu-projeto --path /caminho/do/projeto --collection minha-colecao --workers 8 --verbose
```

#### Quais são as funcionalidades do indexador do Synapstor?
O indexador do Synapstor oferece diversas funcionalidades:
- Comunicação direta com o Qdrant usando o cliente oficial
- Geração de embeddings usando o modelo sentence-transformers
- Suporte a regras do .gitignore para ignorar arquivos
- Processamento em lote para envio eficiente
- Filtros de metadados (projeto, extensão, etc.)
- Paralelismo para indexação mais rápida
- Geração de IDs determinísticos para evitar duplicação

#### Como configurar o Synapstor para uso com o Cursor?
1. Configure o servidor: `synapstor-server --configure`
2. Defina valores apropriados para `COLLECTION_NAME`, `TOOL_STORE_DESCRIPTION` e `TOOL_FIND_DESCRIPTION`
3. Inicie o servidor com transporte SSE: `synapstor-server --transport sse`
4. No Cursor, adicione o servidor MCP nas configurações, apontando para `http://localhost:8000/sse`

#### Como configurar o Synapstor para uso com o Claude Desktop?
Adicione a seguinte configuração ao arquivo `claude_desktop_config.json`:
```json
{
  "qdrant": {
    "command": "synapstor-server",
    "args": ["--transport", "stdio"],
    "env": {
      "QDRANT_URL": "https://seu-servidor-qdrant:6333",
      "QDRANT_API_KEY": "sua_chave_api",
      "COLLECTION_NAME": "sua-colecao",
      "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
    }
  }
}
```

### Resolução de Problemas

#### O servidor não está iniciando. O que fazer?
Verifique se:
1. Todas as dependências estão instaladas: `pip install -e .`
2. O arquivo .env está configurado corretamente: `synapstor-server --create-env`
3. As variáveis de ambiente obrigatórias estão definidas
4. A conexão com o Qdrant está funcionando
5. A coleção especificada existe ou pode ser criada

#### Como verificar se a conexão com o Qdrant está funcionando?
Você pode testar a conexão iniciando o servidor com nível de log DEBUG:
```bash
LOG_LEVEL=DEBUG synapstor-server
```
Isso mostrará informações detalhadas sobre a tentativa de conexão.

#### O indexador está muito lento. Como melhorar o desempenho?
Aumente o número de workers paralelos:
```bash
synapstor-indexer --project meu-projeto --path /caminho/do/projeto --workers 16
```
Ou reduza o tamanho máximo dos arquivos indexados:
```bash
synapstor-indexer --project meu-projeto --path /caminho/do/projeto --max-file-size 1
```

#### Como saber se meu projeto foi indexado corretamente?
Após a indexação, o indexador mostrará estatísticas sobre o processo. Você também pode testar uma consulta:
```bash
synapstor-indexer --project meu-projeto --path /caminho/do/projeto --query "exemplo de consulta"
```
Isso executará a indexação e uma busca de teste.
