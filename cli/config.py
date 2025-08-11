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

# Import i18n support
from src.synapstor.i18n import set_language
from src.synapstor.i18n import _ as translate
from src.synapstor.i18n.languages import Language

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("synapstor-config")


class InteractiveConfigurator:
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

    def _read_existing_env(self) -> Dict[str, str]:
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
            logger.error(translate("cli.config.errors.read_failed", error=str(e)))

        return env_vars

    def _request_values(
        self, variables: List[str], existing: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Interactively requests values for variables

        Args:
            variables: List of variables to be requested
            existing: Dictionary with existing values

        Returns:
            Dict[str, str]: Dictionary with values provided by the user
        """
        values = {}

        # Descriptions for each variable (localized)
        descriptions = {
            "QDRANT_URL": translate("cli.config.descriptions.qdrant_url"),
            "QDRANT_API_KEY": translate("cli.config.descriptions.qdrant_api_key"),
            "COLLECTION_NAME": translate("cli.config.descriptions.collection_name"),
            "QDRANT_LOCAL_PATH": translate("cli.config.descriptions.qdrant_local_path"),
            "EMBEDDING_PROVIDER": translate(
                "cli.config.descriptions.embedding_provider"
            ),
            "EMBEDDING_MODEL": translate("cli.config.descriptions.embedding_model"),
            "QDRANT_SEARCH_LIMIT": translate("cli.config.descriptions.search_limit"),
            "TOOL_STORE_DESCRIPTION": translate("cli.config.descriptions.tool_store"),
            "TOOL_FIND_DESCRIPTION": translate("cli.config.descriptions.tool_find"),
            "LOG_LEVEL": translate("cli.config.descriptions.log_level"),
        }

        # Default values for each variable
        defaults = {
            "QDRANT_URL": "http://localhost:6333",
            "COLLECTION_NAME": "synapstor",
            "EMBEDDING_PROVIDER": "FASTEMBED",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
            "QDRANT_SEARCH_LIMIT": "10",
            "LOG_LEVEL": "INFO",
        }

        print("\n" + "=" * 50)
        print(translate("cli.config.titles.configuration"))
        print("=" * 50)

        for var in variables:
            current_value = existing.get(var, "")
            default = current_value or defaults.get(var, "")

            if var in REQUIRED_VARS:
                print(f"\n{var} ({translate('cli.config.labels.required')})")
            else:
                print(f"\n{var} ({translate('cli.config.labels.optional')})")

            if var in descriptions:
                print(f"  {descriptions[var]}")

            if default:
                prompt = f"  {translate('cli.config.prompts.value_with_default', default=default)}: "
            else:
                prompt = f"  {translate('cli.config.prompts.value')}: "

            new_value = input(prompt)

            # If the user doesn't enter anything, use the default value
            values[var] = new_value or default

        return values

    def _save_env(self, values: Dict[str, str]) -> bool:
        """
        Saves the values to the .env file

        Args:
            values: Dictionary with values to be saved

        Returns:
            bool: True if the file was successfully saved, False otherwise
        """
        try:
            with open(self.env_path, "w", encoding="utf-8") as f:
                f.write(f"# {translate('cli.config.file_headers.title')}\n")
                f.write(f"# {translate('cli.config.file_headers.auto_generated')}\n\n")

                # Writes the required variables first
                f.write(f"# {translate('cli.config.file_headers.required_section')}\n")
                for var in REQUIRED_VARS:
                    f.write(f"{var}={values.get(var, '')}\n")

                # Writes the optional variables
                f.write(
                    f"\n# {translate('cli.config.file_headers.optional_section')}\n"
                )
                for var in OPTIONAL_VARS:
                    if var in values and values[var]:
                        f.write(f"{var}={values.get(var, '')}\n")

            logger.info(
                translate("cli.config.messages.env_saved", path=str(self.env_path))
            )
            return True

        except Exception as e:
            logger.error(translate("cli.config.errors.save_failed", error=str(e)))
            return False

    def configure(self) -> bool:
        """
        Executes the interactive configuration

        Returns:
            bool: True if the configuration was successfully completed, False otherwise
        """
        # Reads existing values if the file already exists
        existing_values = self._read_existing_env()

        # Requests required values
        print(translate("cli.config.messages.configure_required"))
        required_values = self._request_values(REQUIRED_VARS, existing_values)

        # Asks if you want to configure optional values
        print(translate("cli.config.prompts.configure_optional"))
        configure_optional = input().strip().lower() in ["y", "yes", "s", "sim"]

        if configure_optional:
            print(translate("cli.config.messages.configure_optional"))
            optional_values = self._request_values(OPTIONAL_VARS, existing_values)
        else:
            optional_values = {
                var: existing_values.get(var, "") for var in OPTIONAL_VARS
            }

        # Combines all values
        all_values = {**required_values, **optional_values}

        # Saves the values to the .env file
        return self._save_env(all_values)

    def check_dependencies(self) -> bool:
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

        print(translate("cli.config.messages.checking_dependencies"))
        missing = []

        for pkg_name, import_name in deps.items():
            try:
                __import__(import_name)
                print(f"✅ {pkg_name}")
            except ImportError:
                print(f"❌ {pkg_name}")
                missing.append(pkg_name)

        if missing:
            print(
                translate(
                    "cli.config.messages.installing_dependencies",
                    deps=", ".join(missing),
                )
            )
            import subprocess

            for pkg in missing:
                try:
                    print(
                        translate("cli.config.messages.installing_package", package=pkg)
                    )
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", pkg],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    print(
                        translate("cli.config.messages.package_installed", package=pkg)
                    )
                except Exception as e:
                    print(
                        translate(
                            "cli.config.errors.package_install_failed",
                            package=pkg,
                            error=str(e),
                        )
                    )
                    return False

            print(translate("cli.config.messages.all_dependencies_installed"))
        else:
            print(translate("cli.config.messages.dependencies_already_installed"))

        return True


def main():
    """
    Main function for command-line usage
    """
    import argparse

    # Configure language from environment variable
    lang_code = os.environ.get("SYNAPSTOR_LANGUAGE", "en")
    if lang_code == "pt":
        set_language(Language.PORTUGUESE)
    else:
        set_language(Language.ENGLISH)

    parser = argparse.ArgumentParser(description=translate("cli.config.description"))
    parser.add_argument(
        "--env-file",
        default=".env",
        help=translate("cli.config.args.env_file_help"),
    )

    args = parser.parse_args()

    env_path = Path(args.env_file)

    print("=" * 50)
    print(translate("cli.config.titles.main_title"))
    print("=" * 50)
    print(translate("cli.config.messages.intro"))

    configurator = InteractiveConfigurator(env_path)

    # Check dependencies first
    if not configurator.check_dependencies():
        print(translate("cli.config.errors.dependency_check_failed"))
        print(translate("cli.config.messages.manual_install_instruction"))
        print("pip install mcp[cli] fastembed qdrant-client pydantic python-dotenv")
        return 1

    # Run interactive configuration
    if configurator.configure():
        print(translate("cli.config.messages.configuration_success"))
        print(
            translate("cli.config.messages.env_file_location", path=env_path.absolute())
        )
        print(translate("cli.config.messages.server_start_options"))
        print("  synapstor-server")
        print(translate("cli.config.messages.or"))
        print("  python -m synapstor.main")
        return 0
    else:
        print(translate("cli.config.errors.configuration_failed"))
        return 1


# Backward compatibility alias
ConfiguradorInterativo = InteractiveConfigurator


if __name__ == "__main__":
    sys.exit(main())
