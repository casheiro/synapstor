import argparse
import sys

from synapstor.env_loader import setup_environment


def main():
    """
    Main entry point for the synapstor script defined
    in pyproject.toml. It runs the MCP server with a specific transport
    protocol.
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
    from synapstor.server import mcp

    print(f"Iniciando servidor MCP com transporte: {args.transport}")
    mcp.run(transport=args.transport)
