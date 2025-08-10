"""
Utility for generating deterministic IDs in Synapstor.

This module provides functions to generate consistent IDs based on metadata,
allowing document updates without duplication.
"""

import hashlib
from typing import Dict, Any
from synapstor.i18n import _


def generate_deterministic_id(metadata: Dict[str, Any]) -> str:
    """
    Generates a deterministic ID based on document metadata.

    The ID is generated using a combination of project and absolute path,
    ensuring that the same file always has the same ID.

    Args:
        metadata: Dictionary of metadata containing at least 'project' and 'absolute_path'
                 or other unique identifiers

    Returns:
        Hexadecimal string representing a unique and deterministic ID
    """
    # Extract identification data
    project = metadata.get("project", "") or metadata.get("projeto", "")
    absolute_path = metadata.get("absolute_path", "") or metadata.get(
        "caminho_absoluto", ""
    )

    # If there's no project and path, try to use other identifiers
    if not (project and absolute_path):
        content_hash = ""
        # Try to use filename if available
        filename = metadata.get("filename", "") or metadata.get("nome_arquivo", "")
        if filename:
            content_hash += f"file:{filename};"

        # Use any available metadata to create a unique string
        for key in sorted(metadata.keys()):
            if key not in [
                "project",
                "projeto",
                "absolute_path",
                "caminho_absoluto",
                "filename",
                "nome_arquivo",
            ]:
                value = str(metadata[key])
                if value:
                    content_hash += f"{key}:{value};"
    else:
        # Use the project+absolute_path combination as the main identifier
        content_hash = f"{project}:{absolute_path}"

    # If there's still nothing for hash, return None
    if not content_hash:
        raise ValueError(_("id_generator.insufficient_metadata"))

    # Calculate the MD5 hash of the identification string
    return hashlib.md5(content_hash.encode("utf-8")).hexdigest()


def extract_numeric_id(id_hex: str, digits: int = 8) -> int:
    """
    Extracts a numeric ID from a hexadecimal hash.

    Useful for systems that prefer numeric IDs instead of strings.

    Args:
        id_hex: Hexadecimal hash
        digits: Number of hexadecimal characters to use (default 8)

    Returns:
        Integer value extracted from the hash
    """
    return int(id_hex[:digits], 16)


# Backward compatibility aliases
gerar_id_determinista = generate_deterministic_id
extrair_id_numerico = extract_numeric_id
