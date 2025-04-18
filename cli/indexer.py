#!/usr/bin/env python3
"""
Script wrapper para o indexador do Synapstor

Este script serve como interface de linha de comando para o indexador,
permitindo acessá-lo através do comando `synapstor-indexer`.

Wrapper script for the Synapstor indexer

This script serves as a command-line interface for the indexer,
allowing access through the `synapstor-indexer` command.
"""

import os
import sys

# Adiciona o diretório raiz ao path para importar o módulo
# Adds the root directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    """
    Função principal que chama o indexador original

    Esta função simplesmente passa todos os argumentos para o indexador original,
    mantendo todas as flags e funcionalidades disponíveis.

    Main function that calls the original indexer

    This function simply passes all arguments to the original indexer,
    maintaining all available flags and functionality.
    """
    try:
        # Importa a função principal do indexador
        # Imports the main function of the indexer
        from synapstor.tools.indexer import main as indexer_main

        # Executa a função principal do indexador com os mesmos argumentos
        # Runs the main function of the indexer with the same arguments
        return indexer_main()
    except Exception as e:
        print(f"\n❌ Erro ao executar o indexador: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
