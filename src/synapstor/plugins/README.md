# Sistema de Plugins do Synapstor

## 🌎 Idioma / Language

- [Português 🇧🇷](#português)
- [English 🇺🇸](#english)

---

<a name="português"></a>
# Português 🇧🇷

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

- **Arquivos**: Use o prefixo `tool_` seguido de um nome descritivo (ex: `tool_changelog.py`)
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

### Gerador de Changelog (`tool_changelog.py`)

Gera changelogs automaticamente a partir do histórico de commits Git, seguindo o padrão Conventional Commits.

```python
# Geração de changelog
await gerar_changelog(ctx, desde="v1.0.0", ate="HEAD", arquivo_saida="CHANGELOG.md")
# Retorno: "Changelog gerado com sucesso em: CHANGELOG.md"

# Verificação de conformidade dos commits
await verificar_commits(ctx, desde="v1.0.0", detalhado=True)
# Retorno: Lista com estatísticas e detalhes de conformidade dos commits
```

Características principais:
- Análise de mensagens de commit no formato Conventional Commits
- Geração automática da próxima versão seguindo regras SemVer
- Agrupamento de commits por tipo (feat, fix, refactor, etc.)
- Destaque para breaking changes
- Manutenção incremental do changelog (preserva versões anteriores)

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

---

<a name="english"></a>
# English 🇺🇸

This module implements a flexible plugin system that allows extending Synapstor with new functionalities without modifying the core code.

## Overview

The Synapstor plugin system was designed with the following objectives:

- **Extensibility**: Add new tools without modifying the core code
- **Modularity**: Each plugin is an independent module with a single responsibility
- **Simplicity**: Simple and straightforward API for plugin developers
- **Dynamic Loading**: Plugins are discovered and loaded automatically at startup

## Architecture

### Plugin Loader (`__init__.py`)

The main module implements the plugin discovery and loading mechanism:

```python
def load_plugin_tools(server_instance: Any) -> List[str]:
    """
    Loads all tools from available plugins.
    """
    # Discovers and imports files with "tool_" prefix
    # Calls the setup_tools() function of each plugin
    # Returns the list of registered tools
```

### Anatomy of a Plugin

Each plugin is an independent Python module that:

1. Defines one or more tool functions
2. Implements the `setup_tools()` function to register its tools with the server

## Plugin Development

### Reference Template

The `tool_boilerplate.py` file provides a complete template for plugin development:

```python
async def my_tool(
    ctx: Context,
    input: str,
    option: int = 1,
    additional_parameters: Optional[List[str]] = None,
) -> str:
    """Tool implementation"""
    # ...

def setup_tools(server) -> List[str]:
    """Registers tools with the server"""
    server.add_tool(
        my_tool,
        name="my-tool",
        description="Tool description"
    )
    return ["my-tool"]
```

### Creating a New Plugin

1. **File Name**: Create a new file with the `tool_` prefix (e.g., `tool_my_tool.py`)

2. **Tool Implementation**: Define your tool functions as asynchronous functions:

```python
async def my_tool(ctx: Context, param1: str, param2: int = 0) -> str:
    """
    Detailed description of the tool.

    :param ctx: The request context.
    :param param1: Description of the first parameter.
    :param param2: Description of the second parameter.
    :return: Result of the operation.
    """
    # Implement the tool logic
    return f"Result: {param1}, {param2}"
```

3. **Tool Registration**: Implement the `setup_tools` function:

```python
def setup_tools(server) -> List[str]:
    """Registers the tools provided by this plugin."""
    server.add_tool(
        my_tool,
        name="my-tool",
        description="Concise description of the tool."
    )
    return ["my-tool"]
```

## Guidelines and Best Practices

### Naming Conventions

- **Files**: Use the `tool_` prefix followed by a descriptive name (e.g., `tool_changelog.py`)
- **Functions**: Use `snake_case` for definitions and `kebab-case` for exposure
- **Parameters**: Clear and self-descriptive names

### Tool Parameters

- **First Parameter**: Should always be `ctx: Context`
- **Explicit Types**: All parameters should have explicit types
- **Default Values**: Optional parameters should have default values
- **Documentation**: Detailed docstrings for each parameter

### Tool Returns

- **Return Types**: `str` for single message, `List[str]` for multiple messages
- **Formatting**: Formatted text for better readability
- **Errors**: Return clear and useful error messages

### Logging and Debugging

- **Internal Logging**: Use `logger.info()`, `logger.debug()`, etc.
- **Client Debug**: Use `await ctx.debug()` for debug messages

## Available Plugins

### Changelog Generator (`tool_changelog.py`)

Automatically generates changelogs from the Git commit history, following the Conventional Commits standard.

```python
# Changelog generation
await generate_changelog(ctx, since="v1.0.0", until="HEAD", output_file="CHANGELOG.md")
# Return: "Changelog successfully generated in: CHANGELOG.md"

# Commit compliance verification
await verify_commits(ctx, since="v1.0.0", detailed=True)
# Return: List with statistics and details of commit compliance
```

Key features:
- Analysis of commit messages in Conventional Commits format
- Automatic generation of the next version following SemVer rules
- Grouping of commits by type (feat, fix, refactor, etc.)
- Highlighting breaking changes
- Incremental changelog maintenance (preserves previous versions)

### Example Template (`tool_boilerplate.py`)

Provides a reference model for plugin development.

```python
# Usage
await my_tool(ctx, input="example", option=2)
# Return: "example processed (x2)"

# Auxiliary tool
await auxiliary_tool(ctx, query="category1")
# Return: ["Category: category1", "  - item1", "  - item2", "  - item3"]
```

## Security and Considerations

1. **Input Validation**: Always validate user inputs
2. **Error Handling**: Use try/except to catch and handle errors
3. **Resources**: Be mindful of resource usage (memory, CPU, network)
4. **Dependencies**: Minimize external dependencies and document the necessary ones

## Contributing

To contribute new plugins:

1. Follow the template and development guidelines
2. Properly document all parameters and behaviors
3. Add usage examples to the README
4. Ensure the plugin works correctly in all use cases
