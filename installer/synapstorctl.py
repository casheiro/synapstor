#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitário de linha de comando para gerenciar o Synapstor

Este utilitário facilita a configuração, inicialização, e uso do Synapstor,
incluindo a instalação dos scripts no PATH do sistema.

Uso:
    synapstorctl setup       - Configura o Synapstor e adiciona ao PATH
    synapstorctl start       - Inicia o servidor Synapstor
    synapstorctl stop        - Para o servidor Synapstor (se estiver rodando)
    synapstorctl status      - Verifica o status do servidor
    synapstorctl path        - Adiciona os comandos do Synapstor ao PATH
    synapstorctl index       - Indexa um projeto no Synapstor
    synapstorctl uninstall   - Desinstala o Synapstor do sistema
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path

def get_script_dir():
    """Obtém o diretório de scripts do Synapstor"""
    # 1. Verifica na pasta atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(os.path.dirname(current_dir), 'scripts')
    
    # 2. Verifica na pasta ~/.synapstor/
    user_dir = os.path.join(os.path.expanduser('~'), '.synapstor')
    
    if os.path.exists(scripts_dir):
        return scripts_dir
    elif os.path.exists(user_dir):
        return user_dir
    
    return None

def configurar_path():
    """Configura o PATH para incluir os comandos do Synapstor"""
    scripts_dir = get_script_dir()
    
    if not scripts_dir:
        print("❌ Scripts de configuração não encontrados.")
        print("Execute 'pip install synapstor' para instalar o pacote.")
        return False
    
    # Executa o script apropriado para a plataforma
    if os.name == 'nt':  # Windows
        ps_script = os.path.join(scripts_dir, 'add_path.ps1')
        bat_script = os.path.join(scripts_dir, 'add_path.bat')
        
        if os.path.exists(ps_script):
            try:
                print(f"Executando script PowerShell: {ps_script}")
                subprocess.run(
                    ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_script],
                    check=True
                )
                return True
            except subprocess.SubprocessError as e:
                print(f"❌ Erro ao executar o script PowerShell: {e}")
        
        if os.path.exists(bat_script):
            try:
                print(f"Executando script Batch: {bat_script}")
                subprocess.run([bat_script], shell=True, check=True)
                return True
            except subprocess.SubprocessError as e:
                print(f"❌ Erro ao executar o script Batch: {e}")
    else:  # Linux/macOS
        sh_script = os.path.join(scripts_dir, 'add_path.sh')
        
        if os.path.exists(sh_script):
            try:
                print(f"Executando script shell: {sh_script}")
                os.chmod(sh_script, 0o755)  # Torna executável
                subprocess.run(['bash', sh_script], check=True)
                return True
            except subprocess.SubprocessError as e:
                print(f"❌ Erro ao executar o script shell: {e}")
    
    print("❌ Não foi possível configurar o PATH automaticamente.")
    return False

def iniciar_servidor():
    """Inicia o servidor Synapstor"""
    try:
        print("Iniciando servidor Synapstor...")
        
        # Verifica se o comando synapstor-server está disponível
        try:
            # Usa which no Linux/macOS e where no Windows
            if os.name == 'nt':
                subprocess.run(['where', 'synapstor-server'], check=True, capture_output=True)
            else:
                subprocess.run(['which', 'synapstor-server'], check=True, capture_output=True)
        except subprocess.SubprocessError:
            print("⚠️ O comando synapstor-server não está no PATH.")
            print("Tentando localizar o comando...")
            
            # Tenta encontrar o script no pacote instalado
            import site
            scripts_dir = os.path.join(site.USER_BASE, 'Scripts' if os.name == 'nt' else 'bin')
            
            if os.name == 'nt':
                synapstor_cmd = os.path.join(scripts_dir, 'synapstor-server.exe')
                if not os.path.exists(synapstor_cmd):
                    synapstor_cmd = os.path.join(scripts_dir, 'synapstor-server.bat')
                if not os.path.exists(synapstor_cmd):
                    synapstor_cmd = os.path.join(scripts_dir, 'synapstor-server')
            else:
                synapstor_cmd = os.path.join(scripts_dir, 'synapstor-server')
            
            if not os.path.exists(synapstor_cmd):
                print("❌ Não foi possível encontrar o comando synapstor-server.")
                return False
            
            # Executa o comando com o caminho completo
            subprocess.Popen([synapstor_cmd], shell=True)
            print("✅ Servidor iniciado!")
            return True
        
        # Inicia o servidor em segundo plano
        if os.name == 'nt':
            subprocess.Popen(['start', '/b', 'synapstor-server'], shell=True)
        else:
            subprocess.Popen(['synapstor-server', '&'], shell=True)
        
        print("✅ Servidor iniciado!")
        return True
    except Exception as e:
        print(f"❌ Erro ao iniciar o servidor: {e}")
        return False

def parar_servidor():
    """Para o servidor Synapstor se estiver em execução"""
    try:
        print("Parando servidor Synapstor...")
        
        # Encontra o processo pelo nome
        if os.name == 'nt':
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'synapstor-server.exe'], check=True)
                print("✅ Servidor parado!")
                return True
            except subprocess.SubprocessError:
                print("⚠️ Servidor não encontrado ou já está parado.")
        else:
            try:
                subprocess.run(['pkill', '-f', 'synapstor-server'], check=True)
                print("✅ Servidor parado!")
                return True
            except subprocess.SubprocessError:
                print("⚠️ Servidor não encontrado ou já está parado.")
        
        return False
    except Exception as e:
        print(f"❌ Erro ao parar o servidor: {e}")
        return False

def verificar_status():
    """Verifica o status do servidor Synapstor"""
    try:
        print("Verificando status do servidor Synapstor...")
        
        # Verifica se o processo está em execução
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq synapstor-server.exe'], 
                                   capture_output=True, text=True)
            if 'synapstor-server.exe' in result.stdout:
                print("✅ Servidor está rodando!")
                return True
        else:
            result = subprocess.run(['pgrep', '-f', 'synapstor-server'], 
                                   capture_output=True, text=True)
            if result.stdout.strip():
                print("✅ Servidor está rodando!")
                return True
        
        print("⚠️ Servidor não está rodando.")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar status do servidor: {e}")
        return False

def indexar_projeto(projeto=None, caminho=None):
    """Indexa um projeto no Synapstor"""
    try:
        # Se projeto ou caminho não foram fornecidos, solicita ao usuário
        if not projeto:
            print("Nome do projeto a ser indexado:")
            projeto = input().strip()
        
        if not caminho:
            print("Caminho completo do projeto:")
            caminho = input().strip()
            
            # Converte para caminho absoluto se for relativo
            if not os.path.isabs(caminho):
                caminho = os.path.abspath(os.path.join(os.getcwd(), caminho))
        
        if not os.path.exists(caminho):
            print(f"❌ O caminho {caminho} não existe.")
            return False
        
        print(f"Indexando projeto '{projeto}' no caminho: {caminho}")
        
        # Executa o comando de indexação
        try:
            subprocess.run(['synapstor-index', '--project', projeto, '--path', caminho], check=True)
            print("✅ Indexação concluída com sucesso!")
            return True
        except subprocess.SubprocessError as e:
            print(f"❌ Erro durante a indexação: {e}")
            return False
    except Exception as e:
        print(f"❌ Erro ao indexar projeto: {e}")
        return False

def setup():
    """Configura o Synapstor completo"""
    try:
        # Verifica se o pacote synapstor está instalado
        try:
            import synapstor
            print("✅ Pacote Synapstor encontrado.")
        except ImportError:
            print("❌ Pacote Synapstor não está instalado.")
            print("Execute 'pip install synapstor' para instalar o pacote.")
            return False
        
        # Chama o script de configuração do Synapstor
        print("Executando configuração do Synapstor...")
        try:
            # Tenta encontrar o comando synapstor-setup
            if os.name == 'nt':
                result = subprocess.run(['where', 'synapstor-setup'], 
                                      capture_output=True, text=True, check=True)
                setup_cmd = result.stdout.strip().split('\n')[0]
            else:
                result = subprocess.run(['which', 'synapstor-setup'], 
                                      capture_output=True, text=True, check=True)
                setup_cmd = result.stdout.strip()
            
            # Executa o comando de setup
            subprocess.run([setup_cmd], check=True)
            return True
        except subprocess.SubprocessError:
            print("⚠️ Comando synapstor-setup não encontrado no PATH.")
            
            # Tenta chamar o módulo diretamente
            try:
                subprocess.run([sys.executable, '-m', 'cli.setup'], check=True)
                return True
            except subprocess.SubprocessError as e:
                print(f"❌ Erro ao executar a configuração: {e}")
                
                # Última tentativa: configurar apenas o PATH
                print("Tentando configurar apenas o PATH...")
                return configurar_path()
    except Exception as e:
        print(f"❌ Erro durante a configuração: {e}")
        return False

def desinstalar():
    """Desinstala o Synapstor do sistema"""
    try:
        print("=== Desinstalador do Synapstor ===")
        
        # Confirmação do usuário
        resposta = input("Isso removerá o Synapstor e suas configurações. Continuar? (s/n): ")
        if resposta.lower() != 's':
            print("Desinstalação cancelada.")
            return False
        
        # Execute o script de desinstalação apropriado para a plataforma
        if os.name == 'nt':  # Windows
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uninstall.ps1')
            if os.path.exists(script_path):
                print("Executando script de desinstalação para Windows...")
                subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path], check=True)
            else:
                print("Script de desinstalação não encontrado. Executando desinstalação básica...")
                subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', 'synapstor'], check=True)
        else:  # Linux/macOS
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uninstall.sh')
            if os.path.exists(script_path):
                print("Executando script de desinstalação para Linux/macOS...")
                # Torna o script executável
                os.chmod(script_path, 0o755)
                subprocess.run(['bash', script_path], check=True)
            else:
                print("Script de desinstalação não encontrado. Executando desinstalação básica...")
                subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', 'synapstor'], check=True)
        
        print("✅ Synapstor desinstalado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao desinstalar o Synapstor: {e}")
        print("Tente executar manualmente: pip uninstall -y synapstor")
        return False

def uninstall_command():
    """Ponto de entrada para o comando synapstor-uninstall"""
    return 0 if desinstalar() else 1

def main():
    """Função principal que gerencia os comandos do utilitário"""
    parser = argparse.ArgumentParser(description='Utilitário de linha de comando para o Synapstor')
    subparsers = parser.add_subparsers(dest='comando', help='Comando a ser executado')
    
    # Comando setup
    setup_parser = subparsers.add_parser('setup', help='Configura o Synapstor e adiciona ao PATH')
    
    # Comando start
    start_parser = subparsers.add_parser('start', help='Inicia o servidor Synapstor')
    
    # Comando stop
    stop_parser = subparsers.add_parser('stop', help='Para o servidor Synapstor')
    
    # Comando status
    status_parser = subparsers.add_parser('status', help='Verifica o status do servidor')
    
    # Comando path
    path_parser = subparsers.add_parser('path', help='Adiciona os comandos do Synapstor ao PATH')
    
    # Comando index
    index_parser = subparsers.add_parser('index', help='Indexa um projeto no Synapstor')
    index_parser.add_argument('--project', '-p', help='Nome do projeto')
    index_parser.add_argument('--path', '-d', help='Caminho do projeto')
    
    # Comando uninstall
    uninstall_parser = subparsers.add_parser('uninstall', help='Desinstala o Synapstor do sistema')
    
    args = parser.parse_args()
    
    # Se nenhum comando for especificado, mostra a ajuda
    if not args.comando:
        parser.print_help()
        return
    
    # Executa o comando solicitado
    if args.comando == 'setup':
        setup()
    elif args.comando == 'start':
        iniciar_servidor()
    elif args.comando == 'stop':
        parar_servidor()
    elif args.comando == 'status':
        verificar_status()
    elif args.comando == 'path':
        configurar_path()
    elif args.comando == 'index':
        indexar_projeto(args.project, args.path)
    elif args.comando == 'uninstall':
        desinstalar()

if __name__ == '__main__':
    main() 