"""
Utility for generating deterministic IDs in Synapstor.

This module provides functions to generate consistent IDs based on metadata,
allowing document updates without duplication.
"""

import hashlib
from typing import Dict, Any


def gerar_id_determinista(metadata: Dict[str, Any]) -> str:
    """
    Generates a deterministic ID based on document metadata.

    The ID is generated using a combination of project and absolute path,
    ensuring that the same file always has the same ID.

    Args:
        metadata: Dictionary of metadata containing at least 'projeto' and 'caminho_absoluto'
                 or other unique identifiers

    Returns:
        Hexadecimal string representing a unique and deterministic ID
    """
    # Extract identification data
    projeto = metadata.get("projeto", "")
    caminho = metadata.get("caminho_absoluto", "")

    # If there's no project and path, try to use other identifiers
    if not (projeto and caminho):
        content_hash = ""
        # Try to use nome_arquivo if available
        if "nome_arquivo" in metadata:
            content_hash += f"file:{metadata['nome_arquivo']};"

        # Use any available metadata to create a unique string
        for key in sorted(metadata.keys()):
            if key not in ["projeto", "caminho_absoluto", "nome_arquivo"]:
                value = str(metadata[key])
                if value:
                    content_hash += f"{key}:{value};"
    else:
        # Use the project+absolute_path combination as the main identifier
        content_hash = f"{projeto}:{caminho}"

    # If there's still nothing for hash, return None
    if not content_hash:
        raise ValueError("Insufficient metadata to generate deterministic ID")

    # Calculate the MD5 hash of the identification string
    return hashlib.md5(content_hash.encode("utf-8")).hexdigest()


def extrair_id_numerico(id_hex: str, digitos: int = 8) -> int:
    """
    Extracts a numeric ID from a hexadecimal hash.

    Useful for systems that prefer numeric IDs instead of strings.

    Args:
        id_hex: Hexadecimal hash
        digitos: Number of hexadecimal characters to use (default 8)

    Returns:
        Integer value extracted from the hash
    """
    return int(id_hex[:digitos], 16)
