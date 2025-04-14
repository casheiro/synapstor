"""
Utilitário para geração de IDs determinísticos no Synapstor.

Este módulo fornece funções para gerar IDs consistentes baseados em metadados,
permitindo atualização de documentos sem duplicação.
"""

import hashlib
from typing import Dict, Any


def gerar_id_determinista(metadata: Dict[str, Any]) -> str:
    """
    Gera um ID determinístico baseado nos metadados do documento.
    
    O ID é gerado usando uma combinação de projeto e caminho absoluto,
    garantindo que o mesmo arquivo sempre tenha o mesmo ID.
    
    Args:
        metadata: Dicionário de metadados contendo pelo menos 'projeto' e 'caminho_absoluto'
                 ou outros identificadores únicos
    
    Returns:
        String hexadecimal que representa um ID único e determinístico
    """
    # Extrai dados para identificação
    projeto = metadata.get('projeto', '')
    caminho = metadata.get('caminho_absoluto', '')
    
    # Se não tiver projeto e caminho, tenta usar outros identificadores
    if not (projeto and caminho):
        content_hash = ""
        # Tenta usar nome_arquivo se disponível
        if 'nome_arquivo' in metadata:
            content_hash += f"file:{metadata['nome_arquivo']};"
            
        # Usa qualquer metadados disponível para criar uma string única
        for key in sorted(metadata.keys()):
            if key not in ['projeto', 'caminho_absoluto', 'nome_arquivo']:
                value = str(metadata[key])
                if value:
                    content_hash += f"{key}:{value};"
    else:
        # Usa a combinação projeto+caminho_absoluto como identificador principal
        content_hash = f"{projeto}:{caminho}"
    
    # Se mesmo assim não tiver nada para hash, retorna None
    if not content_hash:
        raise ValueError("Metadados insuficientes para gerar ID determinístico")
    
    # Calcula o hash MD5 da string de identificação
    return hashlib.md5(content_hash.encode('utf-8')).hexdigest()


def extrair_id_numerico(id_hex: str, digitos: int = 8) -> int:
    """
    Extrai um ID numérico a partir de um hash hexadecimal.
    
    Útil para sistemas que preferem IDs numéricos em vez de strings.
    
    Args:
        id_hex: Hash hexadecimal
        digitos: Número de caracteres hexadecimais a usar (padrão 8)
    
    Returns:
        Valor inteiro extraído do hash
    """
    return int(id_hex[:digitos], 16) 