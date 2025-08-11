#!/usr/bin/env python3
"""
Wrapper script for the Synapstor indexer

This script serves as a command-line interface for the indexer,
allowing it to be accessed through the `synapstor-indexer` command.
"""

import os
import sys

# Adds the root directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.synapstor.i18n import set_language
from src.synapstor.i18n.languages import Language


def main():
    """
    Main function that calls the original indexer

    This function simply passes all arguments to the original indexer,
    keeping all flags and functionalities available.
    """
    # Configure language from environment variable
    lang_code = os.environ.get("SYNAPSTOR_LANGUAGE", "en")
    if lang_code == "pt":
        set_language(Language.PORTUGUESE)
    else:
        set_language(Language.ENGLISH)

    try:
        # Import the main function from the indexer
        from src.synapstor.tools.indexer import main as indexer_main

        # Execute the main function of the indexer with the same arguments
        return indexer_main()
    except Exception as e:
        from src.synapstor.i18n import _ as translate

        print(f"\n❌ {translate('common.error')}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
