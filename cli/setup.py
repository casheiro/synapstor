#!/usr/bin/env python3
"""
Script de configuração inicial do Synapstor

Este script é executado quando o usuário executa 'synapstor-setup' após a instalação.
"""

import os
import sys
import shutil
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa o configurador
from cli.config import ConfiguradorInterativo


def main():
    """
    Função principal do script de configuração
    """
    print("=" * 50)
    print("INSTALAÇÃO DO SYNAPSTOR")
    print("=" * 50)

    print("\nIniciando a configuração do Synapstor...")

    # Obtém o diretório atual
    diretorio_atual = Path.cwd()

    # Define o caminho do arquivo .env
    env_path = diretorio_atual / ".env"

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
        # Oferece opções para onde instalar os scripts
        print("\nOnde deseja instalar os scripts? (Escolha uma opção)")
        print(" 1. Diretório atual")
        print(" 2. Diretório de usuário (~/.synapstor/bin)")
        print(" 3. Outro diretório (personalizado)")

        opcao = input("\nOpção: ").strip()

        # Define o diretório de destino com base na opção escolhida
        destino = None

        if opcao == "1":
            destino = diretorio_atual
            print(f"\nScripts serão instalados em: {destino}")
        elif opcao == "2":
            # Criar diretório ~/.synapstor/bin se não existir
            user_dir = Path.home() / ".synapstor" / "bin"
            user_dir.mkdir(parents=True, exist_ok=True)
            destino = user_dir
            print(f"\nScripts serão instalados em: {destino}")

            # Perguntar se deseja adicionar ao PATH (apenas em sistemas Unix-like)
            if os.name != "nt":
                print("\nDeseja adicionar este diretório ao seu PATH? (s/n)")
                add_to_path = input().strip().lower() in ["s", "sim", "y", "yes"]

                if add_to_path:
                    # Detecta o shell do usuário
                    shell_file = None
                    shell = os.environ.get("SHELL", "")

                    if "bash" in shell:
                        shell_file = Path.home() / ".bashrc"
                    elif "zsh" in shell:
                        shell_file = Path.home() / ".zshrc"

                    if shell_file:
                        try:
                            # Adiciona ao path no arquivo de configuração do shell
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
            try:
                destino.mkdir(parents=True, exist_ok=True)
                print(f"\nScripts serão instalados em: {destino}")
            except Exception as e:
                print(f"\n⚠️ Erro ao criar diretório: {e}")
                print("Continuando com o diretório atual...")
                destino = diretorio_atual
        else:
            # Opção inválida, usa o diretório atual
            print("\n⚠️ Opção inválida. Usando o diretório atual.")
            destino = diretorio_atual

        # Cria scripts para diferentes sistemas operacionais
        try:
            # Caminhos para os templates
            template_dir = Path(__file__).parent / "templates"

            # Lista de scripts a serem copiados
            scripts = [
                ("start-synapstor.bat", destino / "start-synapstor.bat"),
                ("Start-Synapstor.ps1", destino / "Start-Synapstor.ps1"),
                ("start-synapstor.sh", destino / "start-synapstor.sh"),
            ]

            # Copia cada script do template para o destino
            for origem_nome, destino_caminho in scripts:
                origem_caminho = template_dir / origem_nome
                try:
                    shutil.copy2(origem_caminho, destino_caminho)

                    # Torna o script shell executável (somente em sistemas Unix-like)
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
