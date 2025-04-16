# Sistema de Plugins do Synapstor

Este módulo implementa um sistema flexível de plugins que permite estender o Synapstor com novas funcionalidades sem modificar o código principal.

## Visão Geral

O sistema de plugins do Synapstor foi projetado com os seguintes objetivos:

- **Extensibilidade**: Adicionar novas ferramentas sem modificar o código principal
- **Modularidade**: Cada plugin é um módulo independente com responsabilidade única
- **Simplicidade**: API simples e direta para desenvolvedores de plugins
- **Carregamento Dinâmico**: Plugins são descobertos e carregados automaticamente na inicialização

## Arquitetura

### Carregador de Plugins (`__init__.py`)

O módulo principal implementa o mecanismo de descoberta e carregamento de plugins:

```python
def load_plugin_tools(server_instance: Any) -> List[str]:
    """
    Carrega todas as ferramentas dos plugins disponíveis.
    """
    # Descobre e importa arquivos com prefixo "tool_"
    # Chama a função setup_tools() de cada plugin
    # Retorna a lista de ferramentas registradas
```

### Anatomia de um Plugin

Cada plugin é um módulo Python independente que:

1. Define uma ou mais funções de ferramenta
2. Implementa a função `setup_tools()` para registrar suas ferramentas no servidor

## Desenvolvimento de Plugins

### Template de Referência

O arquivo `tool_boilerplate.py` fornece um template completo para desenvolvimento de plugins:

```python
async def minha_ferramenta(
    ctx: Context,
    entrada: str,
    opcao: int = 1,
    parametros_adicionais: Optional[List[str]] = None,
) -> str:
    """Implementação da ferramenta"""
    # ...

def setup_tools(server) -> List[str]:
    """Registra as ferramentas no servidor"""
    server.add_tool(
        minha_ferramenta,
        name="minha-ferramenta",
        description="Descrição da ferramenta"
    )
    return ["minha-ferramenta"]
```

### Criando um Novo Plugin

1. **Nome do Arquivo**: Crie um novo arquivo com o prefixo `tool_` (ex: `tool_minha_ferramenta.py`)

2. **Implementação de Ferramentas**: Defina suas funções de ferramenta como funções assíncronas:

```python
async def minha_ferramenta(ctx: Context, param1: str, param2: int = 0) -> str:
    """
    Descrição detalhada da ferramenta.
    
    :param ctx: O contexto da solicitação.
    :param param1: Descrição do primeiro parâmetro.
    :param param2: Descrição do segundo parâmetro.
    :return: Resultado da operação.
    """
    # Implemente a lógica da ferramenta
    return f"Resultado: {param1}, {param2}"
```

3. **Registro de Ferramentas**: Implemente a função `setup_tools`:

```python
def setup_tools(server) -> List[str]:
    """Registra as ferramentas fornecidas por este plugin."""
    server.add_tool(
        minha_ferramenta,
        name="minha-ferramenta",
        description="Descrição concisa da ferramenta."
    )
    return ["minha-ferramenta"]
```

## Diretrizes e Melhores Práticas

### Convenções de Nomenclatura

- **Arquivos**: Use o prefixo `tool_` seguido de um nome descritivo (ex: `tool_conversor.py`)
- **Funções**: Use `snake_case` para definições e `kebab-case` para exposição
- **Parâmetros**: Nomes claros e autodescritivos

### Parâmetros das Ferramentas

- **Primeiro Parâmetro**: Sempre deve ser `ctx: Context`
- **Tipos Explícitos**: Todos os parâmetros devem ter tipos explícitos
- **Valores Padrão**: Parâmetros opcionais devem ter valores padrão
- **Documentação**: Docstrings detalhadas para cada parâmetro

### Retorno das Ferramentas

- **Tipos de Retorno**: `str` para mensagem única, `List[str]` para múltiplas mensagens
- **Formatação**: Texto formatado para melhor legibilidade
- **Erros**: Retorne mensagens de erro claras e úteis

### Logging e Debug

- **Logging Interno**: Use `logger.info()`, `logger.debug()`, etc.
- **Debug ao Cliente**: Use `await ctx.debug()` para mensagens de depuração

## Plugins Disponíveis

### Conversor de Unidades (`tool_conversor.py`)

Converte valores entre diferentes unidades de medida.

```python
# Uso
await conversor(ctx, valor=10, de_unidade="km", para_unidade="mi")
# Retorno: "10 quilômetros = 6.21 milhas"

# Listar unidades disponíveis
await ajuda_conversor(ctx)
```

### Template de Exemplo (`tool_boilerplate.py`)

Fornece um modelo de referência para desenvolvimento de plugins.

```python
# Uso
await minha_ferramenta(ctx, entrada="exemplo", opcao=2)
# Retorno: "exemplo processado (x2)"

# Ferramenta auxiliar
await ferramenta_auxiliar(ctx, consulta="categoria1")
# Retorno: ["Categoria: categoria1", "  - item1", "  - item2", "  - item3"]
```

## Segurança e Considerações

1. **Validação de Entrada**: Sempre valide as entradas do usuário
2. **Tratamento de Erros**: Use try/except para capturar e tratar erros
3. **Recursos**: Seja consciente do uso de recursos (memória, CPU, rede)
4. **Dependências**: Minimize dependências externas e documente as necessárias

## Contribuição

Para contribuir com novos plugins:

1. Siga o template e as diretrizes de desenvolvimento
2. Documente adequadamente todos os parâmetros e comportamentos
3. Adicione exemplos de uso ao README
4. Garanta que o plugin funcione corretamente em todos os casos de uso 