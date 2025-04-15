# Desenvolvendo Ferramentas para o Synapstor

Este guia explica como criar novas ferramentas (plugins) para o Synapstor, permitindo que você estenda as funcionalidades do sistema.

## Visão Geral

O Synapstor permite que você crie e adicione suas próprias ferramentas personalizadas que podem ser acessadas via API e utilizadas por modelos de IA como o Claude. Cada ferramenta é implementada como um plugin Python e registrada no servidor durante a inicialização.

## Estrutura Básica de um Plugin

Os plugins do Synapstor seguem uma estrutura padronizada:

1. Um arquivo Python com prefixo `tool_` na pasta `src/synapstor/plugins/`
2. Funções assíncronas que implementam as ferramentas
3. Uma função `setup_tools()` obrigatória que registra as ferramentas

## Passo a Passo para Criar uma Nova Ferramenta

### 1. Crie um Novo Arquivo de Plugin

Comece copiando o arquivo template (`src/synapstor/plugins/tool_boilerplate.py`) e renomeando-o seguindo o padrão:

```
src/synapstor/plugins/tool_nome_descritivo.py
```

### 2. Defina suas Funções de Ferramenta

Cada ferramenta é implementada como uma função assíncrona com os seguintes requisitos:

- O primeiro parâmetro deve ser sempre `ctx: Context`
- Os parâmetros adicionais definem a interface da ferramenta
- O tipo de retorno deve ser `str` ou `List[str]`
- Inclua uma docstring detalhada que explique o propósito da ferramenta

Exemplo:

```python
async def minha_ferramenta(
    ctx: Context,
    texto: str,
    opcao: int = 1,
) -> str:
    """
    Descrição detalhada do que a ferramenta faz.
    
    :param ctx: O contexto da solicitação MCP.
    :param texto: O texto a ser processado.
    :param opcao: Uma opção de configuração (padrão: 1).
    :return: O resultado do processamento.
    """
    # Implementação da ferramenta
    await ctx.debug(f"Processando: {texto} com opção {opcao}")
    return f"Resultado: {texto} processado com {opcao}"
```

### 3. Implemente a Função setup_tools

Esta função é obrigatória e registra suas ferramentas no servidor:

```python
def setup_tools(server) -> List[str]:
    """
    Registra as ferramentas fornecidas por este plugin.
    """
    logger.info("Registrando minhas ferramentas")
    
    server.add_tool(
        minha_ferramenta,
        name="minha-ferramenta",  # Nome em kebab-case
        description="Descrição curta para listagem."
    )
    
    # Retorne uma lista com os nomes de todas as ferramentas registradas
    return ["minha-ferramenta"]
```

## Validação de Parâmetros

É fundamental validar os parâmetros recebidos antes de executar a lógica principal da ferramenta:

```python
# Validar parâmetros obrigatórios
if not texto:
    return "Erro: O texto não pode ser vazio."

# Validar valores em intervalos válidos
if not (1 <= opcao <= 5):
    return f"Erro: A opção deve estar entre 1 e 5. Valor fornecido: {opcao}"

# Validar formatos específicos
import re
if not re.match(r'^[a-zA-Z0-9_]+$', identificador):
    return "Erro: O identificador deve conter apenas letras, números e underscores."
```

## Logging e Depuração

Utilize o objeto `ctx` para logging e depuração:

```python
# Log para depuração (não visível ao usuário)
await ctx.debug(f"Processando: texto={texto}, opcao={opcao}")

# Registro de erro para depuração
await ctx.debug(f"Erro durante o processamento: {e}")
```

## Tipos de Parâmetros Suportados

Os seguintes tipos de parâmetros são suportados pelas ferramentas:

- `str`: Para textos e strings
- `int`: Para valores inteiros
- `float`: Para valores decimais
- `bool`: Para valores booleanos (verdadeiro/falso)
- `List[str]`: Para listas de strings
- `Optional[Tipo]`: Para parâmetros opcionais

Parâmetros opcionais devem ter um valor padrão ou ser definidos como `Optional`.

## Convenções de Nomenclatura

- **Arquivos**: `tool_nome_descritivo.py`
- **Funções**: Use `snake_case` para definição (ex: `minha_ferramenta`)
- **Nomes de ferramentas**: Use `kebab-case` para exposição (ex: `minha-ferramenta`)
- **Parâmetros**: Use nomes claros e descritivos em português

## Exemplos

### Exemplo 1: Ferramenta Simples (Calculadora)

```python
async def calculadora(
    ctx: Context,
    expressao: str,
) -> str:
    """
    Avalia uma expressão matemática simples.
    
    :param ctx: O contexto da solicitação MCP.
    :param expressao: A expressão matemática a ser avaliada (ex: "2+2*3").
    :return: O resultado da avaliação ou mensagem de erro.
    """
    await ctx.debug(f"Avaliando expressão: {expressao}")
    
    # Validação de segurança
    caracteres_permitidos = set('0123456789+-*/() .')
    if not all(c in caracteres_permitidos for c in expressao):
        return "Erro: A expressão contém caracteres não permitidos."
    
    try:
        # Avalia a expressão de forma segura
        resultado = eval(expressao, {"__builtins__": {}})
        return f"Resultado: {resultado}"
    except Exception as e:
        await ctx.debug(f"Erro ao avaliar expressão: {e}")
        return f"Erro: Não foi possível avaliar a expressão. {str(e)}"
```

### Exemplo 2: Ferramenta Mais Complexa (Conversor de Unidades)

```python
# Definição de dados para conversão
UNIDADES = {
    "comprimento": {
        "m": 1.0,        # metro (unidade base)
        "km": 1000.0,    # quilômetro
        "cm": 0.01,      # centímetro
        "mm": 0.001,     # milímetro
    },
    "peso": {
        "kg": 1.0,       # quilograma (unidade base)
        "g": 0.001,      # grama
        "t": 1000.0,     # tonelada
    }
}

async def conversor(
    ctx: Context,
    valor: float,
    de_unidade: str,
    para_unidade: str,
) -> str:
    """
    Converte valores entre diferentes unidades de medida.
    
    :param ctx: O contexto da solicitação MCP.
    :param valor: O valor a ser convertido.
    :param de_unidade: A unidade de origem (ex: "km", "g").
    :param para_unidade: A unidade de destino (ex: "m", "kg").
    :return: O resultado da conversão ou mensagem de erro.
    """
    await ctx.debug(f"Convertendo {valor} de {de_unidade} para {para_unidade}")
    
    # Encontrar categoria das unidades
    categoria_origem = None
    categoria_destino = None
    
    for categoria, unidades in UNIDADES.items():
        if de_unidade in unidades:
            categoria_origem = categoria
        if para_unidade in unidades:
            categoria_destino = categoria
    
    # Validação
    if categoria_origem is None:
        return f"Erro: Unidade de origem '{de_unidade}' não reconhecida."
    if categoria_destino is None:
        return f"Erro: Unidade de destino '{para_unidade}' não reconhecida."
    if categoria_origem != categoria_destino:
        return f"Erro: Não é possível converter entre '{categoria_origem}' e '{categoria_destino}'."
    
    # Conversão
    try:
        # Converter para a unidade base
        valor_base = valor * UNIDADES[categoria_origem][de_unidade]
        # Converter da unidade base para a unidade de destino
        resultado = valor_base / UNIDADES[categoria_origem][para_unidade]
        
        return f"{valor} {de_unidade} = {resultado} {para_unidade}"
    except Exception as e:
        await ctx.debug(f"Erro na conversão: {e}")
        return f"Erro ao realizar a conversão: {str(e)}"
```

## Estrutura Completa de um Plugin

Aqui está um esboço da estrutura completa de um plugin:

```python
import logging
from typing import List, Optional
from synapstor.mcp.context import Context

# Configure o logger
logger = logging.getLogger(__name__)

# Constantes e dados
DADOS = {...}

# Funções auxiliares
def _funcao_interna(param):
    ...

# Função principal da ferramenta
async def minha_ferramenta(ctx, param1, param2=None):
    """Docstring da ferramenta"""
    ...
    return resultado

# Função de registro obrigatória
def setup_tools(server):
    server.add_tool(minha_ferramenta, name="minha-ferramenta", description="...")
    return ["minha-ferramenta"]
```

## Testando sua Ferramenta

Para testar sua ferramenta:

1. Coloque seu arquivo na pasta `src/synapstor/plugins/`
2. Reinicie o servidor Synapstor
3. Verifique nos logs se a ferramenta foi registrada corretamente
4. Teste a ferramenta através da interface de chat ou API

### Solução de Problemas

Se sua ferramenta não estiver funcionando:

1. Verifique os logs do servidor para erros de importação ou execução
2. Confirme que a função `setup_tools()` está retornando os nomes corretos
3. Verifique se todos os parâmetros estão corretamente tipados
4. Teste com valores simples para identificar problemas

### Comandos Úteis

```bash
# Reiniciar o servidor para carregar novas ferramentas
docker restart synapstor

# Verificar logs em busca de erros
docker logs synapstor
```

## Recomendações Finais

1. Mantenha suas ferramentas simples e focadas em uma única tarefa
2. Documente claramente o propósito e uso de cada ferramenta
3. Valide todos os inputs para evitar erros de execução
4. Use logging para facilitar a depuração
5. Siga as convenções de nomenclatura do projeto

## Template e Exemplos

Consulte o arquivo template (`src/synapstor/plugins/tool_boilerplate.py`) e os exemplos existentes na pasta `src/synapstor/plugins/` para obter mais orientações. 