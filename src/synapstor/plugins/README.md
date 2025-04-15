# Sistema de Plugins do Synapstor

Este diretório contém o sistema de plugins do Synapstor, que permite adicionar novas ferramentas ao servidor MCP sem modificar o código principal.

## Como Adicionar Novas Ferramentas

Para adicionar uma nova ferramenta ao servidor MCP, siga estes passos:

1. Crie um arquivo Python no diretório `plugins/` com o prefixo `tool_` (exemplo: `tool_calculadora.py`).

2. Implemente sua ferramenta seguindo este modelo:

```python
"""
Plugin que adiciona [nome da ferramenta] ao Synapstor.

Este plugin adiciona a funcionalidade [descrição resumida].
"""

import logging
from typing import List
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)

async def minha_ferramenta(
    ctx: Context,
    parametro1: str,
    parametro2: int = 10,  # Parâmetros opcionais podem ter valores padrão
) -> str:  # ou List[str] para retornar múltiplas mensagens
    """
    Descrição detalhada da ferramenta.
    
    :param ctx: O contexto da solicitação MCP.
    :param parametro1: Descrição do primeiro parâmetro.
    :param parametro2: Descrição do segundo parâmetro com valor padrão.
    :return: Resultado da operação ou mensagem de erro.
    """
    # Log de debug (não visível para o usuário)
    await ctx.debug(f"Processando: {parametro1}, {parametro2}")
    
    # Implementação da ferramenta
    resultado = f"Processado {parametro1} com valor {parametro2}"
    
    return resultado

def setup_tools(server) -> List[str]:
    """
    Registra as ferramentas fornecidas por este plugin no servidor.
    
    Esta função é chamada automaticamente pelo carregador de plugins.
    
    Args:
        server: A instância do servidor QdrantMCPServer.
        
    Returns:
        List[str]: Lista de nomes das ferramentas registradas.
    """
    logger.info("Registrando minha ferramenta")
    
    # Registra a ferramenta no servidor MCP
    server.add_tool(
        minha_ferramenta,
        name="minha-ferramenta",  # Nome da ferramenta exposto à API
        description="Descrição clara e concisa da ferramenta."
    )
    
    # Retorna os nomes das ferramentas registradas
    return ["minha-ferramenta"]
```

3. O sistema carregará automaticamente sua ferramenta na próxima inicialização do servidor.

## Diretrizes para Desenvolver Ferramentas

1. **Nomes de Arquivos**: Use o prefixo `tool_` para todos os arquivos de plugin.

2. **Função setup_tools**: Cada plugin deve ter uma função `setup_tools(server)` que registra as ferramentas.

3. **Funções Assíncronas**: Todas as ferramentas devem ser definidas como funções assíncronas (`async def`).

4. **Primeiro Parâmetro**: O primeiro parâmetro deve sempre ser `ctx: Context`.

5. **Tipos de Parâmetros**: Todos os parâmetros devem ter tipos explícitos para serem corretamente expostos ao cliente.

6. **Documentação**: Forneça docstrings detalhadas para sua ferramenta e seus parâmetros.

7. **Retorno**: As ferramentas podem retornar `str` para uma única mensagem ou `List[str]` para múltiplas mensagens.

8. **Logging**: Use `await ctx.debug()` para registrar informações úteis para depuração.

## Exemplos

Veja os exemplos de plugins disponíveis:

- `tool_calculadora.py`: Adiciona uma calculadora simples
- `tool_conversor.py`: Adiciona um conversor de unidades
- `tool_tradutor.py`: Adiciona um tradutor de texto

## Melhores Práticas

1. Mantenha suas ferramentas focadas em uma única funcionalidade.
2. Trate erros adequadamente e forneça mensagens de erro úteis.
3. Documente claramente os parâmetros e formato esperado de entrada.
4. Use typing adequadamente para melhorar a experiência do cliente.
5. Evite dependências externas desnecessárias. 