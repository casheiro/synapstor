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


def main():
    """
    Main function that calls the original indexer

    This function simply passes all arguments to the original indexer,
    keeping all flags and functionalities available.
    """
    try:
        # Import the main function from the indexer
        from synapstor.tools.indexer import main as indexer_main

        # Execute the main function of the indexer with the same arguments
        return indexer_main()
    except Exception as e:
        print(f"\n❌ Error running the indexer: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
