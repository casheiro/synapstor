#!/usr/bin/env python3
# uninstall-synapstor.py
# Script independente para desinstalar o Synapstor

import subprocess
import sys

def desinstalar():
    print("Desinstalando Synapstor...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "synapstor"], check=True)
        print("✅ Synapstor removido com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao desinstalar: {e}")
        return False

if __name__ == "__main__":
    desinstalar()
    input("Pressione ENTER para sair...") 