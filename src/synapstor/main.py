import argparse
import sys

from synapstor.env_loader import setup_environment
from synapstor.i18n import get_translator, set_language, SupportedLanguages
from synapstor.settings import I18nSettings


def main():
    """
    Main entry point for the synapstor script defined in pyproject.toml.
    It runs the MCP server with a specific transport protocol.
    """
    # Configure the environment before starting the server
    if not setup_environment():
        print("Error configuring the environment. The MCP server cannot be started.")
        sys.exit(1)
    
    # Configure language
    i18n_settings = I18nSettings()
    language = SupportedLanguages.get_language_by_code(i18n_settings.language)
    set_language(language)
    translator = get_translator()

    # Parse command line arguments to determine the transport protocol
    parser = argparse.ArgumentParser(description="synapstor")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
    )
    args = parser.parse_args()

    # The import is done here to ensure that environment variables are loaded
    # only after we have made the changes
    print(translator.translate("server.starting"))
    try:
        from synapstor.server import mcp

        print(f"Starting MCP server with transport: {args.transport}")
        
        if args.transport == "http":
            # For HTTP transport, use specific configuration
            from synapstor.settings import ServerSettings
            server_settings = ServerSettings()
            print(f"Starting HTTP server at {server_settings.host}:{server_settings.port}")
            mcp.run(transport="http", host=server_settings.host, port=server_settings.port)
        else:
            mcp.run(transport=args.transport)
        
        print(translator.translate("server.started"))
    except ImportError as e:
        print(translator.translate("server.error_starting", error=str(e)))
        sys.exit(1)
