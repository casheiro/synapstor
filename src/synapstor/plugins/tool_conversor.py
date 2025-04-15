"""
Plugin de conversão de unidades para o Synapstor.

Este plugin adiciona uma ferramenta para converter valores entre diferentes 
unidades de medida (comprimento, massa, temperatura e volume).
"""

import logging
from typing import List, Dict, Callable, Union, Tuple
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)

# Dicionário de conversões para comprimento
COMPRIMENTO: Dict[str, Tuple[str, Callable[[float], float]]] = {
    "km": ("quilômetros", lambda x: x),
    "m": ("metros", lambda x: x * 1000),
    "cm": ("centímetros", lambda x: x * 100000),
    "mm": ("milímetros", lambda x: x * 1000000),
    "mi": ("milhas", lambda x: x * 0.621371),
    "ft": ("pés", lambda x: x * 3280.84),
    "in": ("polegadas", lambda x: x * 39370.1),
}

# Dicionário de conversões para massa
MASSA: Dict[str, Tuple[str, Callable[[float], float]]] = {
    "kg": ("quilogramas", lambda x: x),
    "g": ("gramas", lambda x: x * 1000),
    "mg": ("miligramas", lambda x: x * 1000000),
    "lb": ("libras", lambda x: x * 2.20462),
    "oz": ("onças", lambda x: x * 35.274),
}

# Dicionário de conversões para temperatura
# Estas são especiais porque não são conversões lineares simples
def celsius_para_fahrenheit(c: float) -> float:
    return (c * 9/5) + 32

def celsius_para_kelvin(c: float) -> float:
    return c + 273.15

def fahrenheit_para_celsius(f: float) -> float:
    return (f - 32) * 5/9

def fahrenheit_para_kelvin(f: float) -> float:
    return (f - 32) * 5/9 + 273.15

def kelvin_para_celsius(k: float) -> float:
    return k - 273.15

def kelvin_para_fahrenheit(k: float) -> float:
    return (k - 273.15) * 9/5 + 32

# Dicionário de conversões para volume
VOLUME: Dict[str, Tuple[str, Callable[[float], float]]] = {
    "l": ("litros", lambda x: x),
    "ml": ("mililitros", lambda x: x * 1000),
    "gal": ("galões", lambda x: x * 0.264172),
    "qt": ("quartos", lambda x: x * 1.05669),
    "pt": ("pints", lambda x: x * 2.11338),
    "cup": ("xícaras", lambda x: x * 4.22675),
    "oz_fl": ("onças fluidas", lambda x: x * 33.814),
}

# Mapeamento de categorias
CATEGORIAS = {
    "comprimento": COMPRIMENTO,
    "massa": MASSA,
    "volume": VOLUME,
}

# Conversões de temperatura (caso especial)
TEMPERATURA = {
    "c_para_f": celsius_para_fahrenheit,
    "c_para_k": celsius_para_kelvin,
    "f_para_c": fahrenheit_para_celsius,
    "f_para_k": fahrenheit_para_kelvin,
    "k_para_c": kelvin_para_celsius,
    "k_para_f": kelvin_para_fahrenheit,
}

async def conversor(
    ctx: Context,
    valor: float,
    de_unidade: str,
    para_unidade: str
) -> str:
    """
    Converte um valor entre diferentes unidades de medida.
    
    Suporta conversões de comprimento, massa, temperatura e volume.
    
    :param ctx: O contexto da solicitação MCP.
    :param valor: O valor numérico a ser convertido.
    :param de_unidade: A unidade de origem (ex: 'km', 'kg', 'c', 'l').
    :param para_unidade: A unidade de destino (ex: 'm', 'g', 'f', 'ml').
    :return: O resultado da conversão ou uma mensagem de erro.
    """
    await ctx.debug(f"Convertendo {valor} de {de_unidade} para {para_unidade}")
    
    # Normaliza as unidades para minúsculas
    de_unidade = de_unidade.lower()
    para_unidade = para_unidade.lower()
    
    # Tratamento especial para temperatura
    if de_unidade in ['c', 'f', 'k'] and para_unidade in ['c', 'f', 'k']:
        return await _converter_temperatura(ctx, valor, de_unidade, para_unidade)
    
    # Conversão regular para outras categorias
    return await _converter_regular(ctx, valor, de_unidade, para_unidade)

async def _converter_temperatura(
    ctx: Context,
    valor: float,
    de_unidade: str,
    para_unidade: str
) -> str:
    """Função auxiliar para converter temperatura."""
    # Se as unidades são iguais, não há conversão
    if de_unidade == para_unidade:
        return f"{valor} {_obter_nome_temperatura(de_unidade)}"
    
    # Define a chave de conversão
    chave = f"{de_unidade}_para_{para_unidade}"
    
    # Verifica se a conversão é suportada
    if chave in TEMPERATURA:
        resultado = TEMPERATURA[chave](valor)
        resultado_formatado = _formatar_numero(resultado)
        
        de_nome = _obter_nome_temperatura(de_unidade)
        para_nome = _obter_nome_temperatura(para_unidade)
        
        return f"{valor} {de_nome} = {resultado_formatado} {para_nome}"
    
    return f"Conversão de {de_unidade} para {para_unidade} não suportada."

def _obter_nome_temperatura(unidade: str) -> str:
    """Retorna o nome completo da unidade de temperatura."""
    if unidade == 'c':
        return "graus Celsius (°C)"
    elif unidade == 'f':
        return "graus Fahrenheit (°F)"
    elif unidade == 'k':
        return "Kelvin (K)"
    return unidade

async def _converter_regular(
    ctx: Context,
    valor: float,
    de_unidade: str,
    para_unidade: str
) -> str:
    """Função auxiliar para converter unidades regulares."""
    # Procura a categoria das unidades
    categoria_de = None
    categoria_para = None
    
    for categoria, unidades in CATEGORIAS.items():
        if de_unidade in unidades:
            categoria_de = categoria
        if para_unidade in unidades:
            categoria_para = categoria
    
    # Verifica se ambas as unidades pertencem à mesma categoria
    if categoria_de is None or categoria_para is None:
        return f"Unidade não reconhecida: {'de_unidade' if categoria_de is None else 'para_unidade'}"
    
    if categoria_de != categoria_para:
        return f"Não é possível converter entre {categoria_de} e {categoria_para}."
    
    # Se as unidades são iguais, não há conversão
    if de_unidade == para_unidade:
        return f"{valor} {CATEGORIAS[categoria_de][de_unidade][0]}"
    
    try:
        # Converte para a unidade base da categoria (normalmente a primeira)
        # Para comprimento: km -> m -> destino
        # Para massa: kg -> g -> destino
        # Para volume: l -> ml -> destino
        unidades = CATEGORIAS[categoria_de]
        
        # Primeiro, converte para a unidade base (primeira entrada no dicionário)
        unidade_base = list(unidades.keys())[0]
        
        # Se a unidade de origem não é a base, converte para a base
        valor_base = valor
        if de_unidade != unidade_base:
            # Inverte a função de conversão (de -> base)
            # Exemplo: m -> km seria dividir por 1000
            fator = unidades[de_unidade][1](1) / unidades[unidade_base][1](1)
            valor_base = valor / fator
        
        # Converte da base para a unidade de destino
        resultado = unidades[para_unidade][1](valor_base)
        
        # Formata o resultado para exibição
        resultado_formatado = _formatar_numero(resultado)
        
        # Obtém os nomes completos das unidades
        de_nome = unidades[de_unidade][0]
        para_nome = unidades[para_unidade][0]
        
        return f"{valor} {de_nome} = {resultado_formatado} {para_nome}"
    except Exception as e:
        await ctx.debug(f"Erro na conversão: {e}")
        return f"Erro ao realizar a conversão: {str(e)}"

def _formatar_numero(valor: float) -> str:
    """Formata um número para exibição, removendo zeros desnecessários."""
    if valor == int(valor):
        return str(int(valor))
    else:
        # Limita a 4 casas decimais e remove zeros à direita
        return f"{valor:.4f}".rstrip('0').rstrip('.')

def listar_conversoes_suportadas() -> str:
    """Lista todas as conversões suportadas."""
    resultado = ["Conversões suportadas:"]
    
    # Temperatura (caso especial)
    resultado.append("\nTemperatura:")
    resultado.append("  c - Celsius")
    resultado.append("  f - Fahrenheit")
    resultado.append("  k - Kelvin")
    
    # Outras categorias
    for categoria, unidades in CATEGORIAS.items():
        resultado.append(f"\n{categoria.capitalize()}:")
        for codigo, (nome, _) in unidades.items():
            resultado.append(f"  {codigo} - {nome}")
    
    return "\n".join(resultado)

async def ajuda_conversor(
    ctx: Context,
) -> str:
    """
    Exibe a ajuda do conversor de unidades.
    
    Lista todas as unidades suportadas pelo conversor.
    
    :param ctx: O contexto da solicitação MCP.
    :return: Lista de unidades suportadas.
    """
    await ctx.debug("Solicitação de ajuda do conversor")
    return listar_conversoes_suportadas()

def setup_tools(server) -> List[str]:
    """
    Registra as ferramentas fornecidas por este plugin no servidor.
    
    Args:
        server: A instância do servidor QdrantMCPServer.
        
    Returns:
        List[str]: Lista de nomes das ferramentas registradas.
    """
    logger.info("Registrando ferramenta de conversão de unidades")
    
    # Registra a ferramenta de conversão
    server.add_tool(
        conversor,
        name="conversor",
        description="Converte valores entre diferentes unidades de medida (ex: km para m, kg para g, C para F)."
    )
    
    # Registra a ferramenta de ajuda
    server.add_tool(
        ajuda_conversor,
        name="ajuda-conversor",
        description="Exibe a lista de todas as unidades suportadas pelo conversor."
    )
    
    return ["conversor", "ajuda-conversor"] 