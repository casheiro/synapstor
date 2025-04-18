#!/usr/bin/env python3
"""
Script to run mypy with correctly configured PYTHONPATH.
"""

import os
import sys
import subprocess


def main():
    # Add directories to PYTHONPATH
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] += os.pathsep + os.path.abspath(".")
        os.environ["PYTHONPATH"] += os.pathsep + os.path.abspath("./src")
    else:
        os.environ["PYTHONPATH"] = (
            os.path.abspath(".") + os.pathsep + os.path.abspath("./src")
        )

    # Get arguments passed to the script (except the first one which is the script name)
    args = sys.argv[1:]

    # Run mypy with the arguments and configured PYTHONPATH
    result = subprocess.run(["mypy"] + args)

    # Return mypy's exit code
    return result.returncode


# When executed directly as a script or with python -m
if __name__ == "__main__":
    sys.exit(main())
