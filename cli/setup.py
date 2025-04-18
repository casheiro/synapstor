#!/usr/bin/env python3
"""
Script de configuração inicial do Synapstor

Este script é executado quando o usuário executa 'synapstor-setup' após a instalação.

Initial setup script for Synapstor

This script is executed when the user runs 'synapstor-setup' after installation.
"""

import os
import sys
import shutil
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o módulo
# Adds the root directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa o configurador
# Imports the configurator
from cli.config import ConfiguradorInterativo


def main():
    """
    Função principal do script de configuração

    Main function of the setup script
    """
    print("=" * 50)
    print("INSTALAÇÃO DO SYNAPSTOR")
    print("=" * 50)

    print("\nIniciando a configuração do Synapstor...")

    # Obtém o diretório atual
    # Gets the current directory
    diretorio_atual = Path.cwd()

    # Define o caminho do arquivo .env
    # Defines the path of the .env file
    env_path = diretorio_atual / ".env"

    # Cria o configurador
    # Creates the configurator
    configurador = ConfiguradorInterativo(env_path)

    # Verifica dependências
    # Checks dependencies
    if not configurador.verificar_dependencias():
        print("\n❌ Falha ao verificar ou instalar dependências.")
        return 1

    # Pergunta se deseja criar um script para iniciar facilmente o servidor
    # Asks if you want to create a script to easily start the server
    print("\nDeseja criar scripts para iniciar facilmente o servidor? (s/n)")
    criar_scripts = input().strip().lower() in ["s", "sim", "y", "yes"]

    if criar_scripts:
        # Oferece opções para onde instalar os scripts
        # Offers options for where to install the scripts
        print("\nOnde deseja instalar os scripts? (Escolha uma opção)")
        print(" 1. Diretório atual")
        print(" 2. Diretório de usuário (~/.synapstor/bin)")
        print(" 3. Outro diretório (personalizado)")

        opcao = input("\nOpção: ").strip()

        # Define o diretório de destino com base na opção escolhida
        # Defines the destination directory based on the chosen option
        destino = None

        if opcao == "1":
            destino = diretorio_atual
            print(f"\nScripts serão instalados em: {destino}")
        elif opcao == "2":
            # Criar diretório ~/.synapstor/bin se não existir
            # Creates the ~/.synapstor/bin directory if it doesn't exist
            user_dir = Path.home() / ".synapstor" / "bin"
            user_dir.mkdir(parents=True, exist_ok=True)
            destino = user_dir
            print(f"\nScripts serão instalados em: {destino}")

            # Perguntar se deseja adicionar ao PATH (apenas em sistemas Unix-like)
            # Asks if you want to add to PATH (only on Unix-like systems)
            if os.name != "nt":
                print("\nDeseja adicionar este diretório ao seu PATH? (s/n)")
                add_to_path = input().strip().lower() in ["s", "sim", "y", "yes"]

                if add_to_path:
                    # Detecta o shell do usuário
                    # Detects the user's shell
                    shell_file = None
                    shell = os.environ.get("SHELL", "")

                    if "bash" in shell:
                        shell_file = Path.home() / ".bashrc"
                    elif "zsh" in shell:
                        shell_file = Path.home() / ".zshrc"

                    if shell_file:
                        try:
                            # Adiciona ao path no arquivo de configuração do shell
                            # Adds to path in the shell configuration file
                            with open(shell_file, "a") as f:
                                f.write("\n# Adicionado pelo instalador do Synapstor\n")
                                f.write(f'export PATH="$PATH:{destino}"\n')
                            print(f"✅ Adicionado ao PATH em {shell_file}")
                        except Exception as e:
                            print(f"⚠️ Não foi possível adicionar ao PATH: {e}")
                    else:
                        print(
                            "⚠️ Não foi possível determinar o arquivo de configuração do shell."
                        )
                        print(f'Adicione manualmente: export PATH="$PATH:{destino}"')

        elif opcao == "3":
            custom_dir = input("\nDigite o caminho completo para o diretório: ").strip()
            destino = Path(custom_dir)

            # Tenta criar o diretório se ele não existir
            # Tries to create the directory if it doesn't exist
            try:
                destino.mkdir(parents=True, exist_ok=True)
                print(f"\nScripts serão instalados em: {destino}")
            except Exception as e:
                print(f"\n⚠️ Erro ao criar diretório: {e}")
                print("Continuando com o diretório atual...")
                destino = diretorio_atual
        else:
            # Opção inválida, usa o diretório atual
            # Invalid option, uses the current directory
            print("\n⚠️ Opção inválida. Usando o diretório atual.")
            destino = diretorio_atual

        # Cria scripts para diferentes sistemas operacionais
        # Creates scripts for different operating systems
        try:
            # Caminhos para os templates
            # Paths for the templates
            template_dir = Path(__file__).parent / "templates"

            # Lista de scripts a serem copiados
            # List of scripts to be copied
            scripts = [
                ("start-synapstor.bat", destino / "start-synapstor.bat"),
                ("Start-Synapstor.ps1", destino / "Start-Synapstor.ps1"),
                ("start-synapstor.sh", destino / "start-synapstor.sh"),
            ]

            # Copia cada script do template para o destino
            # Copies each script from the template to the destination
            for origem_nome, destino_caminho in scripts:
                origem_caminho = template_dir / origem_nome
                try:
                    shutil.copy2(origem_caminho, destino_caminho)

                    # Torna o script shell executável (somente em sistemas Unix-like)
                    # Makes the shell script executable (only on Unix-like systems)
                    if origem_nome.endswith(".sh") and os.name != "nt":
                        try:
                            os.chmod(destino_caminho, 0o755)
                        except Exception:
                            pass
                except Exception as e:
                    print(f"\n⚠️ Erro ao copiar {origem_nome}: {e}")

            print("\n✅ Scripts de inicialização criados com sucesso!")
        except Exception as e:
            print(f"\n⚠️ Ocorreu um erro ao criar os scripts: {e}")

    # Executa a configuração interativa
    # Executes the interactive configuration
    print("\nVamos configurar o Synapstor...")
    if configurador.configurar():
        print("\n✅ Configuração concluída com sucesso!")
        print(f"Arquivo .env foi criado em: {env_path.absolute()}")

        if criar_scripts:
            print("\nVocê pode iniciar o servidor com um dos scripts criados:")

            if opcao == "1" or opcao == "3":
                print("  - Windows: start-synapstor.bat ou Start-Synapstor.ps1")
                print("  - Linux/macOS: ./start-synapstor.sh")
            elif opcao == "2":
                print(
                    f"  - Windows: {destino}/start-synapstor.bat ou {destino}/Start-Synapstor.ps1"
                )
                print(f"  - Linux/macOS: {destino}/start-synapstor.sh")
                print(f"\nCaminho completo do diretório: {destino}")
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
