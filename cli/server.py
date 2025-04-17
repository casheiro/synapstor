#!/usr/bin/env python3
"""
Script wrapper para o servidor Synapstor

Este script serve como interface de linha de comando para o servidor,
permitindo acessá-lo através do comando `synapstor-server` com opções adicionais.
"""

import os
import sys
import argparse
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    """
    Função principal para iniciar o servidor

    Fornece opções adicionais como:
    - Escolha do protocolo de transporte
    - Seleção de arquivo .env personalizado
    - Criação de arquivo .env se não existir
    """
    parser = argparse.ArgumentParser(description="Inicia o servidor Synapstor")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Protocolo de transporte (stdio ou sse, padrão: stdio)",
    )
    parser.add_argument(
        "--env-file", default=".env", help="Caminho para o arquivo .env (padrão: .env)"
    )
    parser.add_argument(
        "--create-env",
        action="store_true",
        help="Cria um arquivo .env de exemplo se não existir",
    )
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Configura o ambiente antes de iniciar o servidor",
    )

    args = parser.parse_args()

    # Se o arquivo .env não existir e --create-env foi especificado, cria o arquivo
    if args.create_env and not os.path.exists(args.env_file):
        from synapstor.env_loader import create_env_file_template

        create_env_file_template()
        print(f"✅ Arquivo .env de exemplo criado como {args.env_file}")
        print("Por favor, edite-o com suas configurações e execute novamente.")
        return 0

    # Se --configure foi especificado, executa o configurador interativo
    if args.configure:
        from cli.config import ConfiguradorInterativo

        env_path = Path(args.env_file)
        print("🔧 Configurando o Synapstor antes de iniciar o servidor...")
        configurador = ConfiguradorInterativo(env_path)
        if not configurador.configurar():
            print("❌ Falha ao configurar o Synapstor. O servidor não será iniciado.")
            return 1
        print("✅ Configuração concluída. Iniciando o servidor...")

    # Importa e executa o servidor MCP
    try:
        # Configura os argumentos para o servidor principal
        if "--env-file" in sys.argv:
            # O módulo principal não aceita --env-file, então o removemos
            # mas o arquivo .env já foi selecionado durante a execução
            sys.argv.remove("--env-file")
            if args.env_file in sys.argv:
                sys.argv.remove(args.env_file)

        if "--create-env" in sys.argv:
            sys.argv.remove("--create-env")

        if "--configure" in sys.argv:
            sys.argv.remove("--configure")

        # Executa o servidor principal
        from synapstor.main import main as mcp_main

        return mcp_main()
    except Exception as e:
        print(f"❌ Erro ao iniciar o servidor: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
