#!/usr/bin/env python3
"""
Initial setup script for Synapstor

This script is executed when the user runs 'synapstor-setup' after installation.
"""

import os
import sys
import shutil
from pathlib import Path

# Adds the root directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import i18n support and configurator
from src.synapstor.i18n import set_language
from src.synapstor.i18n import _ as translate
from src.synapstor.i18n.languages import Language
from cli.config import InteractiveConfigurator


def main():
    """
    Main function of the setup script
    """
    # Configure language from environment variable
    lang_code = os.environ.get("SYNAPSTOR_LANGUAGE", "en")
    if lang_code == "pt":
        set_language(Language.PORTUGUESE)
    else:
        set_language(Language.ENGLISH)

    print("=" * 50)
    print(translate("cli.setup.title"))
    print("=" * 50)

    print(translate("cli.setup.messages.starting_setup"))

    # Get the current directory
    current_directory = Path.cwd()

    # Define the path of the .env file
    env_path = current_directory / ".env"

    # Create the configurator
    configurator = InteractiveConfigurator(env_path)

    # Check dependencies
    if not configurator.check_dependencies():
        print(translate("cli.setup.messages.dependency_check_failed"))
        return 1

    # Ask if you want to create a script to easily start the server
    print(translate("cli.setup.prompts.create_scripts"))
    create_scripts = input().strip().lower() in ["y", "yes"]

    if create_scripts:
        # Offers options for where to install the scripts
        print(translate("cli.setup.prompts.script_location"))
        print(translate("cli.setup.options.current_directory"))
        print(translate("cli.setup.options.user_directory"))
        print(translate("cli.setup.options.custom_directory"))

        option = input(translate("cli.setup.prompts.option_input")).strip()

        # Define the destination directory based on the chosen option
        destination = None

        if option == "1":
            destination = current_directory
            print(translate("cli.setup.messages.scripts_destination", path=destination))
        elif option == "2":
            # Create directory ~/.synapstor/bin if it doesn't exist
            user_dir = Path.home() / ".synapstor" / "bin"
            user_dir.mkdir(parents=True, exist_ok=True)
            destination = user_dir
            print(translate("cli.setup.messages.scripts_destination", path=destination))

            # Ask if you want to add to PATH (only on Unix-like systems)
            if os.name != "nt":
                print(translate("cli.setup.prompts.add_to_path"))
                add_to_path = input().strip().lower() in ["y", "yes"]

                if add_to_path:
                    # Detect the user's shell
                    shell_file = None
                    shell = os.environ.get("SHELL", "")

                    if "bash" in shell:
                        shell_file = Path.home() / ".bashrc"
                    elif "zsh" in shell:
                        shell_file = Path.home() / ".zshrc"

                    if shell_file:
                        try:
                            # Add to path in the shell configuration file
                            with open(shell_file, "a") as f:
                                f.write("\n# Added by the Synapstor installer\n")
                                f.write(f'export PATH="$PATH:{destination}"\n')
                            print(
                                translate(
                                    "cli.setup.messages.added_to_path", file=shell_file
                                )
                            )
                        except Exception as e:
                            print(
                                translate(
                                    "cli.setup.warnings.path_add_failed", error=str(e)
                                )
                            )
                    else:
                        print(translate("cli.setup.warnings.shell_not_detected"))
                        print(
                            translate(
                                "cli.setup.messages.manual_path_instruction",
                                path=destination,
                            )
                        )

        elif option == "3":
            custom_dir = input(translate("cli.setup.prompts.custom_path")).strip()
            destination = Path(custom_dir)

            # Try to create the directory if it doesn't exist
            try:
                destination.mkdir(parents=True, exist_ok=True)
                print(
                    translate(
                        "cli.setup.messages.scripts_destination", path=destination
                    )
                )
            except Exception as e:
                print(
                    translate(
                        "cli.setup.warnings.directory_creation_failed", error=str(e)
                    )
                )
                print(translate("cli.setup.messages.using_current_directory"))
                destination = current_directory
        else:
            # Invalid option, use the current directory
            print(translate("cli.setup.warnings.invalid_option"))
            destination = current_directory

        # Create scripts for different operating systems
        try:
            # Paths for templates
            template_dir = Path(__file__).parent / "templates"

            # List of scripts to be copied
            scripts = [
                ("start-synapstor.bat", destination / "start-synapstor.bat"),
                ("Start-Synapstor.ps1", destination / "Start-Synapstor.ps1"),
                ("start-synapstor.sh", destination / "start-synapstor.sh"),
            ]

            # Copy each script from the template to the destination
            for source_name, destination_path in scripts:
                source_path = template_dir / source_name
                try:
                    shutil.copy2(source_path, destination_path)

                    # Make the shell script executable (only on Unix-like systems)
                    if source_name.endswith(".sh") and os.name != "nt":
                        try:
                            os.chmod(destination_path, 0o755)
                        except Exception:
                            pass
                except Exception as e:
                    print(
                        translate(
                            "cli.setup.warnings.script_copy_failed",
                            script=source_name,
                            error=str(e),
                        )
                    )

            print(translate("cli.setup.messages.scripts_created"))
        except Exception as e:
            print(translate("cli.setup.warnings.script_creation_error", error=str(e)))

    # Run the interactive configuration
    print(translate("cli.setup.messages.starting_configuration"))
    if configurator.configure():
        print(translate("cli.setup.messages.configuration_completed"))
        print(
            translate("cli.setup.messages.env_file_created", path=env_path.absolute())
        )

        if create_scripts:
            print(translate("cli.setup.messages.server_start_with_scripts"))

            if option == "1" or option == "3":
                print(translate("cli.setup.messages.windows_scripts"))
                print(translate("cli.setup.messages.unix_scripts"))
            elif option == "2":
                print(
                    translate(
                        "cli.setup.messages.windows_scripts_path", path=destination
                    )
                )
                print(
                    translate("cli.setup.messages.unix_scripts_path", path=destination)
                )
                print(translate("cli.setup.messages.full_path", path=destination))
        else:
            print(translate("cli.setup.messages.server_start_command"))
            print("  synapstor-server")

        print(translate("cli.setup.messages.indexer_usage"))
        print("  synapstor-indexer --project my-project --path /path/to/project")
        return 0
    else:
        print(translate("cli.setup.messages.configuration_failed"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
