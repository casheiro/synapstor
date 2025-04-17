import argparse
import sys

from synapstor.env_loader import setup_environment


def main():
    """
    Ponto de entrada principal para o script synapstor definido
    no pyproject.toml. Ele executa o servidor MCP com um protocolo
    de transporte específico.
    """
    # Configura o ambiente antes de iniciar o servidor
    if not setup_environment():
        print("Erro ao configurar o ambiente. O servidor MCP não pode ser iniciado.")
        sys.exit(1)

    # Parse the command-line arguments to determine the transport protocol.
    parser = argparse.ArgumentParser(description="synapstor")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
    )
    args = parser.parse_args()

    # Import is done here to make sure environment variables are loaded
    # only after we make the changes.
    print("Iniciando servidor MCP...")
    try:
        from synapstor.server import mcp
        
        print(f"Iniciando servidor MCP com transporte: {args.transport}")
        mcp.run(transport=args.transport)
    except ImportError as e:
        print(f"❌ Erro ao iniciar o servidor: {e}")
        sys.exit(1)
