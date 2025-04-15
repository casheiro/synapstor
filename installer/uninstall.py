#!/usr/bin/env python3
"""
Script super simples para desinstalar o Synapstor.

Este script pode ser chamado de qualquer lugar usando:
uninstall-synapstor

Sem confirmações, sem complicações.
"""

import subprocess
import sys

def main():
    """
    Função principal que executa a desinstalação rápida.
    """
    print("🗑️  Desinstalando Synapstor...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "synapstor"], check=True)
        print("✅ Synapstor removido com sucesso!")
        return 0
    except Exception as e:
        print(f"❌ Erro ao desinstalar: {e}")
        return 1

if __name__ == "__main__":
    result = main()
    if sys.platform.startswith('win'):
        input("Pressione ENTER para sair...")
    sys.exit(result) 