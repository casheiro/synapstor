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

# Import the configurator
from cli.config import ConfiguradorInterativo


def main():
    """
    Main function of the setup script
    """
    print("=" * 50)
    print("SYNAPSTOR INSTALLATION")
    print("=" * 50)

    print("\nStarting Synapstor setup...")

    # Get the current directory
    current_directory = Path.cwd()

    # Define the path of the .env file
    env_path = current_directory / ".env"

    # Create the configurator
    configurador = ConfiguradorInterativo(env_path)

    # Check dependencies
    if not configurador.verificar_dependencias():
        print("\n❌ Failed to check or install dependencies.")
        return 1

    # Ask if you want to create a script to easily start the server
    print("\nDo you want to create scripts to easily start the server? (y/n)")
    create_scripts = input().strip().lower() in ["y", "yes"]

    if create_scripts:
        # Offers options for where to install the scripts
        print("\nWhere do you want to install the scripts? (Choose an option)")
        print(" 1. Current directory")
        print(" 2. User directory (~/.synapstor/bin)")
        print(" 3. Other directory (custom)")

        option = input("\nOption: ").strip()

        # Define the destination directory based on the chosen option
        destination = None

        if option == "1":
            destination = current_directory
            print(f"\nScripts will be installed in: {destination}")
        elif option == "2":
            # Create directory ~/.synapstor/bin if it doesn't exist
            user_dir = Path.home() / ".synapstor" / "bin"
            user_dir.mkdir(parents=True, exist_ok=True)
            destination = user_dir
            print(f"\nScripts will be installed in: {destination}")

            # Ask if you want to add to PATH (only on Unix-like systems)
            if os.name != "nt":
                print("\nDo you want to add this directory to your PATH? (y/n)")
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
                            print(f"✅ Added to PATH in {shell_file}")
                        except Exception as e:
                            print(f"⚠️ Could not add to PATH: {e}")
                    else:
                        print("⚠️ Could not determine the shell configuration file.")
                        print(f'Manually add: export PATH="$PATH:{destination}"')

        elif option == "3":
            custom_dir = input("\nEnter the full path to the directory: ").strip()
            destination = Path(custom_dir)

            # Try to create the directory if it doesn't exist
            try:
                destination.mkdir(parents=True, exist_ok=True)
                print(f"\nScripts will be installed in: {destination}")
            except Exception as e:
                print(f"\n⚠️ Error creating directory: {e}")
                print("Continuing with the current directory...")
                destination = current_directory
        else:
            # Invalid option, use the current directory
            print("\n⚠️ Invalid option. Using the current directory.")
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
                    print(f"\n⚠️ Error copying {source_name}: {e}")

            print("\n✅ Startup scripts created successfully!")
        except Exception as e:
            print(f"\n⚠️ An error occurred while creating the scripts: {e}")

    # Run the interactive configuration
    print("\nLet's configure Synapstor...")
    if configurador.configurar():
        print("\n✅ Configuration completed successfully!")
        print(f".env file was created at: {env_path.absolute()}")

        if create_scripts:
            print("\nYou can start the server with one of the created scripts:")

            if option == "1" or option == "3":
                print("  - Windows: start-synapstor.bat or Start-Synapstor.ps1")
                print("  - Linux/macOS: ./start-synapstor.sh")
            elif option == "2":
                print(
                    f"  - Windows: {destination}/start-synapstor.bat or {destination}/Start-Synapstor.ps1"
                )
                print(f"  - Linux/macOS: {destination}/start-synapstor.sh")
                print(f"\nFull directory path: {destination}")
        else:
            print("\nYou can start the server with:")
            print("  synapstor-server")

        print("\nTo index projects, use:")
        print("  synapstor-indexer --project my-project --path /path/to/project")
        return 0
    else:
        print("\n❌ Failed to complete the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
