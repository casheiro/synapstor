"""
Synapstor - Cliente e servidor para armazenamento e busca semântica
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("synapstor")
except PackageNotFoundError:
    __version__ = "0.1.4"  # Versão padrão se não instalado como pacote
