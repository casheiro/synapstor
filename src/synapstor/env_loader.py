#!/usr/bin/env python3
"""
Environment variables loader

This module loads environment variables from the .env file in the project root.
If the file doesn't exist, it tries to use the system environment variables.
"""

import os
import sys
from pathlib import Path
import logging

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("env_loader")

# Define required variables
REQUIRED_VARS = [
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "COLLECTION_NAME",
]

OPTIONAL_VARS = [
    "QDRANT_LOCAL_PATH",
    "EMBEDDING_PROVIDER",
    "EMBEDDING_MODEL",
    "QDRANT_SEARCH_LIMIT",
    "TOOL_STORE_DESCRIPTION",
    "TOOL_FIND_DESCRIPTION",
    "LOG_LEVEL",
]


def find_dotenv():
    """
    Searches for the .env file in the project root or in directories above.

    Returns:
        Path or None: Path to the .env file or None if not found
    """
    # Start in the folder where the script is being executed
    current_dir = Path.cwd()

    # Search for the .env file in the current directory and parent directories
    while True:
        env_path = current_dir / ".env"
        if env_path.exists():
            return env_path

        # Check if we are at the system root
        parent_dir = current_dir.parent
        if parent_dir == current_dir:
            break

        current_dir = parent_dir

    # Try the project package folder
    module_dir = Path(__file__).parent.parent.parent
    env_path = module_dir / ".env"
    if env_path.exists():
        return env_path

    return None


def load_dotenv():
    """
    Loads the .env file if it exists

    Returns:
        bool: True if the .env file was successfully loaded, False otherwise
    """
    try:
        # Try to import python-dotenv
        try:
            from dotenv import load_dotenv as dotenv_load
        except ImportError:
            logger.warning("python-dotenv package not found. Attempting to install...")
            import subprocess

            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "python-dotenv"]
                )
                from dotenv import load_dotenv as dotenv_load

                logger.info("python-dotenv installed successfully!")
            except Exception as e:
                logger.error(f"Error installing python-dotenv: {e}")
                return False

        # Search for the .env file
        dotenv_path = find_dotenv()
        if dotenv_path:
            # Load the .env file
            dotenv_load(dotenv_path=dotenv_path)
            logger.info(f".env file loaded successfully: {dotenv_path}")
            return True
        else:
            logger.warning(".env file not found")
            return False

    except Exception as e:
        logger.error(f"Error loading .env file: {e}")
        return False


def validate_environment():
    """
    Checks if all required environment variables are configured

    Returns:
        bool: True if all required variables are configured, False otherwise
    """
    missing_vars = []

    for var in REQUIRED_VARS:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(
            f"Required environment variables not configured: {', '.join(missing_vars)}"
        )
        return False

    return True


def create_env_file_template():
    """
    Creates a sample .env file in the current folder
    """
    template = """# Qdrant Configuration
# Option 1: Qdrant Cloud
QDRANT_URL=https://your-qdrant-server.cloud.io:6333
QDRANT_API_KEY=your_api_key

# Option 2: Local Qdrant
# QDRANT_LOCAL_PATH=./qdrant_data

# Default collection name (required)
COLLECTION_NAME=your_collection_name

# Embeddings configuration
EMBEDDING_PROVIDER=FASTEMBED
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# MCP tool settings
TOOL_STORE_DESCRIPTION=Store information for later retrieval.
TOOL_FIND_DESCRIPTION=Find related information in the vector database.

# General settings
LOG_LEVEL=INFO
"""

    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(template)
        logger.info("Sample .env file created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating sample .env file: {e}")
        return False


def setup_environment():
    """
    Sets up the environment for the MCP server

    Returns:
        bool: True if the environment was successfully configured, False otherwise
    """
    # Try to load variables from .env file
    env_loaded = load_dotenv()

    # Check if all required variables are configured
    if not validate_environment():
        if not env_loaded:
            logger.error(
                ".env file not found and environment variables not configured."
            )
            print("\n" + "=" * 80)
            print(
                ".env file not found and required environment variables not configured!"
            )
            print(
                "You need to configure the following variables to run the MCP server:"
            )
            for var in REQUIRED_VARS:
                print(f"- {var}")
            print("\nDo you want to create a sample .env file? (y/n)")
            choice = input().strip().lower()
            if choice in ["y", "yes"]:
                success = create_env_file_template()
                if success:
                    print(
                        "Sample .env file created. Please edit it with your settings and run again."
                    )
                else:
                    print("Could not create the sample .env file.")
            print("=" * 80 + "\n")
        return False

    # If we got here, the environment is configured correctly
    logger.info("Environment configured successfully!")
    return True
