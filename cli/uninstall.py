#!/usr/bin/env python3
"""
Script simplificado para desinstalar o Synapstor.

Este script remove rapidamente o pacote Synapstor do sistema,
sem perguntar confirmação adicional.

Uso:
    synapstor-remove
"""

import os
import sys
import subprocess

def desinstalar_rapido():
    """
    Desinstala o Synapstor de forma rápida, sem confirmações adicionais.
    """
    print("Desinstalando Synapstor...")
    
    try:
        # Executa pip uninstall
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "synapstor"], check=True)
        print("✅ Synapstor removido com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao desinstalar: {e}")
        return False

def main():
    """
    Função principal que executa a desinstalação rápida.
    """
    return 0 if desinstalar_rapido() else 1

if __name__ == "__main__":
    sys.exit(main()) 