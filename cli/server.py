#!/usr/bin/env python3
"""
Wrapper script for the Synapstor server

This script serves as a command-line interface for the server,
allowing it to be accessed through the `synapstor-server` command with additional options.
"""

import os
import sys
import argparse
from pathlib import Path

# Adds the root directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.synapstor.i18n import set_language
from src.synapstor.i18n import _ as translate
from src.synapstor.i18n.languages import Language


def main():
    """
    Main function to start the server

    Provides additional options such as:
    - Choice of transport protocol
    - Selection of custom .env file
    - Creation of .env file if it doesn't exist
    """
    # Configure language from environment variable
    lang_code = os.environ.get("SYNAPSTOR_LANGUAGE", "en")
    if lang_code == "pt":
        set_language(Language.PORTUGUESE)
    else:
        set_language(Language.ENGLISH)

    parser = argparse.ArgumentParser(description=translate("cli.server.description"))
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help=translate("cli.server.transport_help"),
    )
    parser.add_argument(
        "--env-file", default=".env", help=translate("cli.server.env_file_help")
    )
    parser.add_argument(
        "--host",
        default=None,
        help=translate("cli.server.host_help"),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=translate("cli.server.port_help"),
    )
    parser.add_argument(
        "--create-env",
        action="store_true",
        help=translate("cli.server.create_env_help"),
    )
    parser.add_argument(
        "--configure",
        action="store_true",
        help=translate("cli.server.configure_help"),
    )

    args = parser.parse_args()

    # If the .env file doesn't exist and --create-env was specified, create the file
    if args.create_env and not os.path.exists(args.env_file):
        from synapstor.env_loader import create_env_file_template

        create_env_file_template()
        print(translate("cli.server.messages.env_created", file=args.env_file))
        print(translate("cli.server.messages.edit_env_message"))
        return 0

    # If --configure was specified, run the interactive configurator
    if args.configure:
        from cli.config import InteractiveConfigurator

        env_path = Path(args.env_file)
        print(translate("cli.server.messages.configuring_server"))
        configurator = InteractiveConfigurator(env_path)
        if not configurator.configure():
            print(translate("cli.server.messages.configuration_failed"))
            return 1
        print(translate("cli.server.messages.configuration_completed"))

    # Import and run the MCP server
    try:
        # Configure arguments for the main server
        if "--env-file" in sys.argv:
            # The main module doesn't accept --env-file, so we remove it
            # but the .env file has already been selected during execution
            sys.argv.remove("--env-file")
            if args.env_file in sys.argv:
                sys.argv.remove(args.env_file)

        if "--create-env" in sys.argv:
            sys.argv.remove("--create-env")

        if "--configure" in sys.argv:
            sys.argv.remove("--configure")

        # Handle HTTP-specific arguments
        if "--host" in sys.argv:
            sys.argv.remove("--host")
            if args.host and args.host in sys.argv:
                sys.argv.remove(args.host)

        if "--port" in sys.argv:
            sys.argv.remove("--port")
            if args.port and str(args.port) in sys.argv:
                sys.argv.remove(str(args.port))

        # Set environment variables for HTTP transport
        if args.transport == "http":
            if args.host:
                os.environ["MCP_SERVER_HOST"] = args.host
            if args.port:
                os.environ["MCP_SERVER_PORT"] = str(args.port)

        # Run the main server
        from synapstor.main import main as mcp_main

        return mcp_main()
    except Exception as e:
        print(translate("cli.server.messages.server_start_error", error=str(e)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
