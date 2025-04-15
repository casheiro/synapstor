#!/usr/bin/env python3
"""
Script de configuração inicial do Synapstor

Este script é executado quando o usuário executa 'synapstor-setup' após a instalação.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa o configurador
from cli.config import ConfiguradorInterativo

def executar_script_path(script_path):
    """
    Executa um script externo para adicionar ao PATH
    Retorna True se o script for executado com sucesso
    """
    if not os.path.exists(script_path):
        print(f"❌ Script não encontrado: {script_path}")
        return False
    
    print(f"Executando script: {script_path}")
    
    try:
        # Windows: scripts .bat e .ps1
        if script_path.endswith('.bat'):
            subprocess.run([script_path], shell=True, check=True)
            return True
            
        elif script_path.endswith('.ps1'):
            # PowerShell requer comandos especiais para execução
            subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                shell=True, check=True
            )
            return True
            
        # Linux/macOS: script .sh
        elif script_path.endswith('.sh'):
            # Torna o script executável se não estiver
            os.chmod(script_path, 0o755)
            # Executa o script
            subprocess.run(['bash', script_path], check=True)
            return True
            
        return False
    except subprocess.SubprocessError as e:
        print(f"❌ Erro ao executar o script: {e}")
        return False

def adicionar_ao_path():
    """
    Adiciona o diretório dos scripts Python ao PATH do sistema
    """
    print("\nAdicionando comandos Synapstor ao PATH do sistema...")
    
    # 1. Tenta executar scripts específicos da plataforma
    scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
    if os.path.exists(scripts_dir):
        # Determina qual script executar com base no sistema operacional
        if os.name == 'nt':  # Windows
            # Tenta o PowerShell primeiro, depois o batch
            ps_script = os.path.join(scripts_dir, 'add_path.ps1')
            bat_script = os.path.join(scripts_dir, 'add_path.bat')
            
            if os.path.exists(ps_script):
                if executar_script_path(ps_script):
                    return True
            
            if os.path.exists(bat_script):
                if executar_script_path(bat_script):
                    return True
        else:  # Linux/macOS
            sh_script = os.path.join(scripts_dir, 'add_path.sh')
            if os.path.exists(sh_script):
                if executar_script_path(sh_script):
                    return True
    
    # 2. Se os scripts não estiverem disponíveis ou falharem, use o método incorporado
    try:
        # Obtém o diretório dos scripts Python
        scripts_dir = None
        
        # Determina o diretório de scripts baseado no ambiente
        if hasattr(sys, 'base_prefix'):
            # Instalação via pip em ambiente virtual
            if sys.base_prefix != sys.prefix:
                scripts_dir = os.path.join(sys.prefix, 'Scripts' if os.name == 'nt' else 'bin')
        
        # Instalação normal via pip
        if not scripts_dir:
            # Tenta obter o diretório de scripts do usuário
            import site
            scripts_dir = os.path.join(site.USER_BASE, 'Scripts' if os.name == 'nt' else 'bin')
            
            # Verifica o diretório específico do Windows Store Python
            if os.name == 'nt' and not os.path.exists(scripts_dir):
                # Tenta encontrar o diretório do Python Store
                appdata = os.environ.get('LOCALAPPDATA', '')
                if appdata:
                    store_scripts = Path(appdata) / 'Packages' / 'PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0' / 'LocalCache' / 'local-packages' / 'Python312' / 'Scripts'
                    if store_scripts.exists():
                        scripts_dir = str(store_scripts)
        
        # Verifica se o diretório de scripts existe
        if not scripts_dir or not os.path.exists(scripts_dir):
            print("⚠️ Não foi possível determinar o diretório de scripts do Python.")
            return False
        
        print(f"Diretório de scripts encontrado: {scripts_dir}")
        
        # Adiciona ao PATH baseado no sistema operacional
        if os.name == 'nt':  # Windows
            # Verifica se o usuário tem permissões de administrador
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                is_admin = False
                
            if is_admin:
                # Usa o registro do Windows para adicionar ao PATH do sistema (requer admin)
                try:
                    import winreg
                    with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as reg:
                        with winreg.OpenKey(reg, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                            path, _ = winreg.QueryValueEx(key, "Path")
                            if scripts_dir not in path.split(';'):
                                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, path + ';' + scripts_dir)
                                print("✅ Adicionado com sucesso ao PATH do sistema!")
                                # Notifica outras aplicações da mudança
                                subprocess.run(['setx', 'PATH', path + ';' + scripts_dir, '/M'], capture_output=True)
                            else:
                                print("✅ O diretório já está no PATH do sistema.")
                except Exception as e:
                    print(f"⚠️ Erro ao modificar o PATH do sistema: {e}")
                    return False
            else:
                # Adiciona ao PATH do usuário (não requer admin)
                try:
                    import winreg
                    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as reg:
                        with winreg.OpenKey(reg, r"Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                            try:
                                path, _ = winreg.QueryValueEx(key, "Path")
                            except:
                                path = ""
                                
                            if scripts_dir not in path.split(';'):
                                if path:
                                    path = path + ';' + scripts_dir
                                else:
                                    path = scripts_dir
                                    
                                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, path)
                                print("✅ Adicionado com sucesso ao PATH do usuário!")
                                # Notifica outras aplicações da mudança
                                subprocess.run(['setx', 'PATH', path], capture_output=True)
                            else:
                                print("✅ O diretório já está no PATH do usuário.")
                except Exception as e:
                    print(f"⚠️ Erro ao modificar o PATH do usuário: {e}")
                    return False
                    
                print("\n⚠️ IMPORTANTE: Para que as alterações tenham efeito completo, você precisa reiniciar seu terminal ou computador.")
        else:  # Unix-like (Linux, macOS)
            # Verifica o shell do usuário
            shell = os.environ.get('SHELL', '')
            home = os.path.expanduser('~')
            
            # Arquivos de configuração baseados no shell
            shell_configs = {
                '/bin/bash': [os.path.join(home, '.bashrc'), os.path.join(home, '.bash_profile')],
                '/bin/zsh': [os.path.join(home, '.zshrc')],
                '/bin/sh': [os.path.join(home, '.profile')],
            }
            
            # Seleciona o arquivo de configuração adequado
            config_file = None
            if shell in shell_configs:
                for file in shell_configs[shell]:
                    if os.path.exists(file):
                        config_file = file
                        break
            
            # Fallback para .profile
            if not config_file:
                config_file = os.path.join(home, '.profile')
            
            # Prepara a linha de exportação de PATH
            export_line = f'\n# Adicionado pelo Synapstor\nexport PATH="$PATH:{scripts_dir}"\n'
            
            # Verifica se a linha já existe no arquivo
            try:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        content = f.read()
                    if scripts_dir not in content:
                        with open(config_file, 'a') as f:
                            f.write(export_line)
                        print(f"✅ Caminho adicionado a {config_file}")
                    else:
                        print(f"✅ O diretório já está configurado em {config_file}")
                else:
                    with open(config_file, 'w') as f:
                        f.write(export_line)
                    print(f"✅ Arquivo {config_file} criado com configuração do PATH")
                
                print(f"\n⚠️ IMPORTANTE: Para aplicar as alterações, execute:\n  source {config_file}")
            except Exception as e:
                print(f"⚠️ Erro ao modificar o arquivo de configuração do shell: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar ao PATH: {e}")
        return False

def instalar_scripts_path():
    """
    Instala os scripts de configuração do PATH no diretório do usuário
    para uso posterior se necessário
    """
    try:
        # Identifica o diretório de scripts no pacote
        package_scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
        
        # Se o diretório não existir, não há scripts para instalar
        if not os.path.exists(package_scripts_dir):
            return
        
        # Define o diretório de instalação na home do usuário
        home_dir = os.path.expanduser('~')
        synapstor_dir = os.path.join(home_dir, '.synapstor')
        
        # Cria o diretório se não existir
        if not os.path.exists(synapstor_dir):
            os.makedirs(synapstor_dir)
        
        # Identifica quais scripts copiar
        scripts = []
        if os.name == 'nt':  # Windows
            scripts = ['add_path.bat', 'add_path.ps1']
        else:  # Linux/macOS
            scripts = ['add_path.sh']
        
        # Copia os scripts
        for script in scripts:
            script_path = os.path.join(package_scripts_dir, script)
            if os.path.exists(script_path):
                dest_path = os.path.join(synapstor_dir, script)
                shutil.copy2(script_path, dest_path)
                
                # Torna o script executável no Linux/macOS
                if os.name != 'nt' and script.endswith('.sh'):
                    os.chmod(dest_path, 0o755)
                
                print(f"Script instalado: {dest_path}")
        
        return synapstor_dir
    except Exception as e:
        print(f"⚠️ Erro ao instalar scripts: {e}")
        return None

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
    
    # Instala os scripts de configuração do PATH para uso posterior
    scripts_dir = instalar_scripts_path()
    
    # Adiciona os comandos ao PATH
    if not adicionar_ao_path():
        print("\n⚠️ Não foi possível adicionar automaticamente os comandos ao PATH.")
        
        # Fornece instruções manuais se os scripts estiverem disponíveis
        if scripts_dir:
            print("\nVocê pode adicionar manualmente os comandos ao PATH executando:")
            if os.name == 'nt':  # Windows
                ps_path = os.path.join(scripts_dir, 'add_path.ps1')
                bat_path = os.path.join(scripts_dir, 'add_path.bat')
                
                if os.path.exists(ps_path):
                    print(f"  powershell -ExecutionPolicy Bypass -File \"{ps_path}\"")
                if os.path.exists(bat_path):
                    print(f"  \"{bat_path}\"")
            else:  # Linux/macOS
                sh_path = os.path.join(scripts_dir, 'add_path.sh')
                if os.path.exists(sh_path):
                    print(f"  bash \"{sh_path}\"")
    
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
        print("  synapstor-index --project meu-projeto --path /caminho/do/projeto")
        return 0
    else:
        print("\n❌ Falha ao completar a configuração.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
