import argparse
import sys

from synapstor.env_loader import setup_environment


def main():
    """
    Main entry point for the synapstor script defined in pyproject.toml.
    It runs the MCP server with a specific transport protocol.
    """
    # Configure the environment before starting the server
    if not setup_environment():
        print("Error configuring the environment. The MCP server cannot be started.")
        sys.exit(1)

    # Parse command line arguments to determine the transport protocol
    parser = argparse.ArgumentParser(description="synapstor")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
    )
    args = parser.parse_args()

    # The import is done here to ensure that environment variables are loaded
    # only after we have made the changes
    print("Starting MCP server...")
    try:
        from synapstor.server import mcp

        print(f"Starting MCP server with transport: {args.transport}")
        mcp.run(transport=args.transport)
    except ImportError as e:
        print(f"❌ Error starting the server: {e}")
        sys.exit(1)
