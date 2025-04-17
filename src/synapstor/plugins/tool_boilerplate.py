"""
TEMPLATE para criação de plugins no Synapstor.

Este arquivo serve como modelo para a criação de novas ferramentas (tools)
para o Synapstor. Use-o como referência e modifique conforme necessário.

INSTRUÇÕES:
1. Copie este arquivo para um novo com prefixo "tool_" seguido do nome da sua ferramenta
2. Implemente suas funções de ferramenta conforme o modelo abaixo
3. Certifique-se de que a função setup_tools() registra todas as suas ferramentas

CONVENÇÕES:
- Nome do arquivo: tool_nome_descritivo.py
- Nome de função exposta: snake_case para definição, kebab-case para exposição
- Parâmetros: Defina tipos explícitos para todos os parâmetros
"""

import logging
from typing import List, Optional
from mcp.server.fastmcp import Context

# Configure o logger
logger = logging.getLogger(__name__)

#############################################################################
# SEÇÃO 1: CONSTANTES E DADOS                                               #
# Defina aqui quaisquer constantes, dicionários ou dados estruturados       #
# que sua ferramenta utilizará.                                             #
#############################################################################

# Exemplo de constantes
VALOR_PADRAO = 42
MENSAGEM_ERRO = "Ocorreu um erro ao processar a solicitação."

# Exemplo de dicionário de dados
DADOS_EXEMPLO = {
    "categoria1": ["item1", "item2", "item3"],
    "categoria2": ["itemA", "itemB", "itemC"],
}

#############################################################################
# SEÇÃO 2: FUNÇÕES AUXILIARES                                               #
# Funções internas que não são expostas diretamente como ferramentas.       #
# Prefixe com underscore para indicar que são funções privadas.             #
#############################################################################


def _validar_entrada(valor: str) -> bool:
    """
    Valida se a entrada fornecida está em um formato aceitável.

    Args:
        valor: O valor a ser validado.

    Returns:
        bool: True se o valor for válido, False caso contrário.
    """
    if not valor or len(valor) < 2:
        return False
    return True


def _processar_dados(dados: str, multiplicador: int = 1) -> str:
    """
    Processa os dados fornecidos de acordo com a lógica da ferramenta.

    Args:
        dados: Os dados a serem processados.
        multiplicador: Um valor para multiplicar o resultado.

    Returns:
        str: O resultado do processamento.
    """
    # Exemplo de processamento
    return f"{dados} processado (x{multiplicador})"


#############################################################################
# SEÇÃO 3: IMPLEMENTAÇÃO DA FERRAMENTA PRINCIPAL                            #
# Aqui você define a função principal que será exposta como ferramenta.     #
# Deve ser uma função assíncrona com tipos de parâmetros explícitos.        #
#############################################################################


async def minha_ferramenta(
    ctx: Context,
    entrada: str,
    opcao: int = 1,
    parametros_adicionais: Optional[List[str]] = None,
) -> str:
    """
    Descrição detalhada da ferramenta principal.

    Explique aqui o propósito da ferramenta, como ela funciona, e
    qualquer informação relevante para o usuário. Esta docstring será
    usada para gerar a descrição da ferramenta visível ao usuário.

    :param ctx: O contexto da solicitação MCP.
    :param entrada: O texto ou valor principal a ser processado.
    :param opcao: Um número que controla o comportamento da ferramenta (padrão: 1).
    :param parametros_adicionais: Lista opcional de parâmetros extras.
    :return: O resultado do processamento ou mensagem de erro.
    """
    # Log para depuração (não visível ao usuário)
    await ctx.debug(
        f"Processando: entrada={entrada}, opcao={opcao}, parametros_adicionais={parametros_adicionais}"
    )

    # Validação dos parâmetros
    if not _validar_entrada(entrada):
        await ctx.debug("Entrada inválida")
        return "Erro: A entrada deve ter pelo menos 2 caracteres."

    if not (1 <= opcao <= 5):
        await ctx.debug(f"Opção inválida: {opcao}")
        return f"Erro: A opção deve estar entre 1 e 5. Valor fornecido: {opcao}"

    # Inicialização de parâmetros opcionais
    if parametros_adicionais is None:
        parametros_adicionais = []

    # Implementação da lógica principal com tratamento de erros
    try:
        # Processamento principal
        resultado = _processar_dados(entrada, opcao)

        # Processamento adicional se houver parâmetros extras
        if parametros_adicionais:
            resultado += f" com parâmetros: {', '.join(parametros_adicionais)}"

        await ctx.debug(f"Processamento concluído: {resultado}")
        return resultado
    except Exception as e:
        # Registre o erro nos logs para depuração
        await ctx.debug(f"Erro durante o processamento: {e}")
        return f"Ocorreu um erro: {str(e)}"


#############################################################################
# SEÇÃO 4: FERRAMENTAS ADICIONAIS (OPCIONAL)                                #
# Se seu plugin oferece múltiplas ferramentas, defina-as aqui.              #
#############################################################################


async def ferramenta_auxiliar(
    ctx: Context,
    consulta: str,
) -> List[str]:
    """
    Uma ferramenta auxiliar que complementa a ferramenta principal.

    Esta ferramenta demonstra como retornar uma lista de strings como resultado.

    :param ctx: O contexto da solicitação MCP.
    :param consulta: O termo de consulta.
    :return: Lista de resultados.
    """
    await ctx.debug(f"Executando consulta: {consulta}")

    # Exemplo de lógica simples
    if not consulta:
        return ["Erro: A consulta não pode ser vazia"]

    # Pesquisa nas categorias
    resultados = []
    for categoria, itens in DADOS_EXEMPLO.items():
        if consulta.lower() in categoria.lower():
            resultados.append(f"Categoria: {categoria}")
            resultados.extend([f"  - {item}" for item in itens])

    if not resultados:
        resultados = ["Nenhum resultado encontrado para a consulta."]

    return resultados


#############################################################################
# SEÇÃO 5: FUNÇÃO DE REGISTRO (OBRIGATÓRIA)                                 #
# Esta função é OBRIGATÓRIA e deve registrar todas as ferramentas           #
# implementadas pelo plugin no servidor.                                    #
#############################################################################


def setup_tools(server) -> List[str]:
    """
    Registra as ferramentas fornecidas por este plugin.

    Esta função é chamada automaticamente pelo Synapstor durante a inicialização.
    Toda ferramenta DEVE ser registrada aqui para ser disponibilizada.

    Args:
        server: A instância do servidor QdrantMCPServer.

    Returns:
        List[str]: Lista com os nomes das ferramentas registradas.
    """
    logger.info("Registrando ferramentas do template")

    # Registrando a ferramenta principal
    server.add_tool(
        minha_ferramenta,
        name="minha-ferramenta",  # Utilize kebab-case para o nome exposto
        description="Ferramenta de exemplo para demonstrar o padrão de plugin.",
    )

    # Registrando a ferramenta auxiliar
    server.add_tool(
        ferramenta_auxiliar,
        name="ferramenta-auxiliar",
        description="Ferramenta auxiliar que demonstra como retornar listas.",
    )

    # IMPORTANTE: Retorne uma lista com os nomes de todas as ferramentas registradas
    return ["minha-ferramenta", "ferramenta-auxiliar"]


#############################################################################
# FIM DO TEMPLATE                                                           #
# Substitua as implementações acima pelas suas próprias ferramentas.        #
# Não se esqueça de atualizar a documentação e os nomes das funções.        #
#############################################################################
