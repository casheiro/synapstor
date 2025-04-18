#!/usr/bin/env python3
"""
Interactive configuration module for Synapstor

This module provides a command-line interface for configuring Synapstor.
"""

import os
import sys
from pathlib import Path
import logging
from typing import Dict, Optional, List
from synapstor.env_loader import REQUIRED_VARS, OPTIONAL_VARS

# Adds the root directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("synapstor-config")


class ConfiguradorInterativo:
    """
    Interactive interface for configuring Synapstor
    """

    def __init__(self, env_path: Optional[Path] = None):
        """
        Initializes the configurator with an optional path to the .env file

        Args:
            env_path: Path to the .env file. If None, .env in the current folder will be used.
        """
        self.env_path = env_path or Path.cwd() / ".env"
        self.config_values: Dict[str, str] = {}

    def _ler_env_existente(self) -> Dict[str, str]:
        """
        Reads an existing .env file

        Returns:
            Dict[str, str]: Dictionary with variables read from the file
        """
        if not self.env_path.exists():
            return {}

        env_vars = {}
        try:
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error reading existing .env file: {e}")

        return env_vars

    def _solicitar_valores(
        self, variaveis: List[str], existentes: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Interactively requests values for variables

        Args:
            variaveis: List of variables to be requested
            existentes: Dictionary with existing values

        Returns:
            Dict[str, str]: Dictionary with values provided by the user
        """
        valores = {}

        # Descriptions for each variable (English)
        descricoes = {
            "QDRANT_URL": "Qdrant server URL (e.g. http://localhost:6333 or https://your-qdrant-server.cloud:6333)",
            "QDRANT_API_KEY": "Qdrant server API key (leave blank for no authentication)",
            "COLLECTION_NAME": "Collection name in Qdrant (e.g. synapstor)",
            "QDRANT_LOCAL_PATH": "Path for local Qdrant storage (optional, leave blank to use the server in the URL)",
            "EMBEDDING_PROVIDER": "Embeddings provider [FASTEMBED]",
            "EMBEDDING_MODEL": "Embeddings model (e.g. sentence-transformers/all-MiniLM-L6-v2)",
            "QDRANT_SEARCH_LIMIT": "Search results limit (e.g. 10)",
            "TOOL_STORE_DESCRIPTION": "Description of the 'store' tool",
            "TOOL_FIND_DESCRIPTION": "Description of the 'find' tool",
            "LOG_LEVEL": "Log level [INFO, DEBUG, WARNING, ERROR]",
        }

        # Default values for each variable
        padroes = {
            "QDRANT_URL": "http://localhost:6333",
            "COLLECTION_NAME": "synapstor",
            "EMBEDDING_PROVIDER": "FASTEMBED",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
            "QDRANT_SEARCH_LIMIT": "10",
            "LOG_LEVEL": "INFO",
        }

        print("\n" + "=" * 50)
        print("Synapstor Configuration")
        print("=" * 50)

        for var in variaveis:
            valor_atual = existentes.get(var, "")
            padrao = valor_atual or padroes.get(var, "")

            if var in REQUIRED_VARS:
                print(f"\n{var} (Required)")
            else:
                print(f"\n{var} (Optional)")

            if var in descricoes:
                print(f"  {descricoes[var]}")

            if padrao:
                prompt = f"  Value [{padrao}]: "
            else:
                prompt = "  Value: "

            novo_valor = input(prompt)

            # If the user doesn't enter anything, use the default value
            valores[var] = novo_valor or padrao

        return valores

    def _salvar_env(self, valores: Dict[str, str]) -> bool:
        """
        Saves the values to the .env file

        Args:
            valores: Dictionary with values to be saved

        Returns:
            bool: True if the file was successfully saved, False otherwise
        """
        try:
            with open(self.env_path, "w", encoding="utf-8") as f:
                f.write("# Synapstor Configuration\n")
                f.write("# Automatically generated file\n\n")

                # Writes the required variables first
                f.write("# Qdrant Configuration (required)\n")
                for var in REQUIRED_VARS:
                    f.write(f"{var}={valores.get(var, '')}\n")

                # Writes the optional variables
                f.write("\n# Optional Settings\n")
                for var in OPTIONAL_VARS:
                    if var in valores and valores[var]:
                        f.write(f"{var}={valores.get(var, '')}\n")

            logger.info(f".env file saved successfully at {self.env_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving .env file: {e}")
            return False

    def configurar(self) -> bool:
        """
        Executes the interactive configuration

        Returns:
            bool: True if the configuration was successfully completed, False otherwise
        """
        # Reads existing values if the file already exists
        valores_existentes = self._ler_env_existente()

        # Requests required values
        print("\nLet's configure the required variables:")
        valores_obrigatorios = self._solicitar_valores(
            REQUIRED_VARS, valores_existentes
        )

        # Asks if you want to configure optional values
        print("\nDo you want to configure optional variables? (y/n)")
        configura_opcionais = input().strip().lower() in ["y", "yes"]

        if configura_opcionais:
            print("\nLet's configure the optional variables:")
            valores_opcionais = self._solicitar_valores(
                OPTIONAL_VARS, valores_existentes
            )
        else:
            valores_opcionais = {
                var: valores_existentes.get(var, "") for var in OPTIONAL_VARS
            }

        # Combines all values
        todos_valores = {**valores_obrigatorios, **valores_opcionais}

        # Saves the values to the .env file
        return self._salvar_env(todos_valores)

    def verificar_dependencias(self) -> bool:
        """
        Checks if all dependencies are installed and installs them if necessary

        Returns:
            bool: True if all dependencies are installed or were successfully installed
        """
        deps = {
            "mcp": "mcp",
            "qdrant-client": "qdrant_client",
            "fastembed": "fastembed",
            "pydantic": "pydantic",
            "python-dotenv": "dotenv",
        }

        print("\nChecking dependencies...")
        missing = []

        for pkg_name, import_name in deps.items():
            try:
                __import__(import_name)
                print(f"✓ {pkg_name}")
            except ImportError:
                print(f"✗ {pkg_name}")
                missing.append(pkg_name)

        if missing:
            print(f"\nInstalling dependencies: {', '.join(missing)}")
            import subprocess

            for pkg in missing:
                try:
                    print(f"Installing {pkg}...")
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", pkg],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    print(f"✓ {pkg} installed successfully")
                except Exception as e:
                    print(f"✗ Error installing {pkg}: {e}")
                    return False

            print("✓ All dependencies installed successfully")
        else:
            print("✓ All dependencies are already installed")

        return True


def main():
    """
    Main function for command-line usage
    """
    import argparse

    parser = argparse.ArgumentParser(description="Synapstor Configurator")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to the .env file (default: .env in the current folder)",
    )

    args = parser.parse_args()

    env_path = Path(args.env_file)

    print("=" * 50)
    print("SYNAPSTOR CONFIGURATION")
    print("=" * 50)
    print("\nThis tool will guide you through configuring Synapstor.")

    configurador = ConfiguradorInterativo(env_path)

    # Check dependencies first
    if not configurador.verificar_dependencias():
        print("\n❌ Failed to check or install dependencies.")
        print("Please try to install manually with:")
        print("pip install mcp[cli] fastembed qdrant-client pydantic python-dotenv")
        return 1

    # Run interactive configuration
    if configurador.configurar():
        print("\n✅ Configuration completed successfully!")
        print(f".env file was created at: {env_path.absolute()}")
        print("\nYou can start the server with:")
        print("  synapstor-server")
        print("or:")
        print("  python -m synapstor.main")
        return 0
    else:
        print("\n❌ Failed to complete the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
