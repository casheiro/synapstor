#!/usr/bin/env python3
"""
Script para iniciar o servidor MCP de forma simplificada
"""

import os
import sys
import argparse

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    parser = argparse.ArgumentParser(description="Inicia o servidor MCP para Qdrant")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse"], 
        default="sse",
        help="Protocolo de transporte (stdio ou sse, padrão: sse)"
    )
    parser.add_argument(
        "--env-file", 
        default=".env",
        help="Caminho para o arquivo .env (padrão: .env)"
    )
    parser.add_argument(
        "--create-env", 
        action="store_true",
        help="Cria um arquivo .env de exemplo se não existir"
    )
    
    args = parser.parse_args()
    
    # Se solicitado, cria o arquivo .env de exemplo
    if args.create_env and not os.path.exists(args.env_file):
        from mcp_server_qdrant.env_loader import create_env_file_template
        create_env_file_template()
        print(f"Arquivo .env de exemplo criado como {args.env_file}")
        print("Por favor, edite-o com suas configurações e execute novamente.")
        return
    
    # Importa o módulo principal
    from mcp_server_qdrant.main import main as mcp_main
    
    # Executa o servidor
    sys.argv = [sys.argv[0], "--transport", args.transport]
    mcp_main()

if __name__ == "__main__":
    main() 