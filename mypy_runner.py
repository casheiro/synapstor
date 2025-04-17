#!/usr/bin/env python3
"""
Script para executar o mypy com PYTHONPATH configurado corretamente.
"""

import os
import sys
import subprocess


def main():
    # Adiciona diretórios ao PYTHONPATH
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] += os.pathsep + os.path.abspath(".")
        os.environ["PYTHONPATH"] += os.pathsep + os.path.abspath("./src")
    else:
        os.environ["PYTHONPATH"] = (
            os.path.abspath(".") + os.pathsep + os.path.abspath("./src")
        )

    # Obtém argumentos passados ao script (exceto o primeiro que é o nome do script)
    args = sys.argv[1:]

    # Executa o mypy com os argumentos e PYTHONPATH configurado
    result = subprocess.run(["mypy"] + args)

    # Retorna o código de saída do mypy
    return result.returncode


# Quando executado diretamente como script ou com python -m
if __name__ == "__main__":
    sys.exit(main())
