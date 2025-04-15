#!/usr/bin/env python3
"""
Script de configuração inicial do Synapstor

Este script é executado quando o usuário executa 'synapstor-setup' após a instalação.
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa o configurador
from cli.config import ConfiguradorInterativo

def main():
    """
    Função principal do script de configuração
    """
    print("="*50)
    print("INSTALAÇÃO DO SYNAPSTOR")
    print("="*50)
    
    print("\nIniciando a configuração do Synapstor...")
    
    # Obtém o diretório atual
    diretorio_atual = Path.cwd()
    
    # Define o caminho do arquivo .env
    env_path = diretorio_atual / '.env'
    
    # Cria o configurador
    configurador = ConfiguradorInterativo(env_path)
    
    # Verifica dependências
    if not configurador.verificar_dependencias():
        print("\n❌ Falha ao verificar ou instalar dependências.")
        return 1
    
    # Pergunta se deseja criar um script para iniciar facilmente o servidor
    print("\nDeseja criar scripts para iniciar facilmente o servidor? (s/n)")
    criar_scripts = input().strip().lower() in ["s", "sim", "y", "yes"]
    
    if criar_scripts:
        # Cria scripts para diferentes sistemas operacionais
        try:
            # Cria script para Windows (.bat)
            with open(diretorio_atual / 'start-synapstor.bat', 'w', encoding='utf-8') as f:
                f.write('@echo off\n')
                f.write('echo Iniciando servidor Synapstor...\n')
                f.write('synapstor-server\n')
                f.write('pause\n')
            
            # Cria script para Windows (PowerShell)
            with open(diretorio_atual / 'Start-Synapstor.ps1', 'w', encoding='utf-8') as f:
                f.write('#!/usr/bin/env pwsh\n\n')
                f.write('Write-Host "Iniciando servidor Synapstor..." -ForegroundColor Cyan\n')
                f.write('synapstor-server\n')
                f.write('Write-Host "Pressione qualquer tecla para continuar..." -NoNewLine\n')
                f.write('$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")\n')
                f.write('Write-Host ""\n')
            
            # Cria script para Linux/macOS (.sh)
            with open(diretorio_atual / 'start-synapstor.sh', 'w', encoding='utf-8') as f:
                f.write('#!/bin/bash\n\n')
                f.write('echo "Iniciando servidor Synapstor..."\n')
                f.write('synapstor-server\n')
            
            # Torna o script shell executável (somente em sistemas Unix-like)
            if os.name != 'nt':  # Se não for Windows
                try:
                    os.chmod(diretorio_atual / 'start-synapstor.sh', 0o755)
                except:
                    pass
                    
            print("\n✅ Scripts de inicialização criados com sucesso!")
        except Exception as e:
            print(f"\n⚠️ Ocorreu um erro ao criar os scripts: {e}")
    
    # Executa a configuração interativa
    print("\nVamos configurar o Synapstor...")
    if configurador.configurar():
        print("\n✅ Configuração concluída com sucesso!")
        print(f"Arquivo .env foi criado em: {env_path.absolute()}")
        
        if criar_scripts:
            print("\nVocê pode iniciar o servidor com um dos scripts criados:")
            print("  - Windows: start-synapstor.bat ou Start-Synapstor.ps1")
            print("  - Linux/macOS: ./start-synapstor.sh")
        else:
            print("\nVocê pode iniciar o servidor com:")
            print("  synapstor-server")
            
        print("\nPara indexar projetos, use:")
        print("  synapstor-indexer --project meu-projeto --path /caminho/do/projeto")
        return 0
    else:
        print("\n❌ Falha ao completar a configuração.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
