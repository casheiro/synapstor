#!/usr/bin/env python3
"""
Script wrapper para o indexador do Synapstor

Este script serve como interface de linha de comando para o indexador,
permitindo acessá-lo através do comando `synapstor-indexer`.
"""

import os
import sys

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    """
    Função principal que chama o indexador original

    Esta função simplesmente passa todos os argumentos para o indexador original,
    mantendo todas as flags e funcionalidades disponíveis.
    """
    try:
        # Importa a função principal do indexador
        from synapstor.tools.indexer import main as indexer_main

        # Executa a função principal do indexador com os mesmos argumentos
        return indexer_main()
    except Exception as e:
        print(f"\n❌ Erro ao executar o indexador: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
