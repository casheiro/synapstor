#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to reindex content in Qdrant without duplication.

This script uses deterministic identifiers for each document,
based on the project name and file path, allowing content to be
reindexed without creating duplications.
"""

import argparse
import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Add i18n support
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.synapstor.i18n import set_language
from src.synapstor.i18n import _ as translate
from src.synapstor.i18n.languages import Language

# Check dependencies
required_dependencies = {
    "dotenv": "python-dotenv",
    "qdrant_client": "qdrant-client[fastembed]",
}

for module, package in required_dependencies.items():
    if importlib.util.find_spec(module) is None:
        print(f"Error: Module '{module}' not found. Install it using:")
        print(f"pip install {package}")
        sys.exit(1)


def generate_deterministic_id(project: str, absolute_path: str) -> int:
    """
    Generates a deterministic ID based on the project name and absolute path of the file.

    Args:
        project: Project name
        absolute_path: Absolute path of the file

    Returns:
        A numeric ID derived from the MD5 hash of the data
    """
    # Create a unique string that identifies this file in this project
    identifier = f"{project}:{absolute_path}"

    # Generate MD5 hash of the identifier
    hash_md5 = hashlib.md5(identifier.encode()).hexdigest()

    # Convert first 8 characters of the hash to integer
    # (avoiding collisions with very low probability)
    return int(hash_md5[:8], 16)


def send_to_qdrant(
    client: QdrantClient,
    collection_name: str,
    text: str,
    metadata: Dict,
    dry_run: bool = False,
) -> Optional[int]:
    """
    Sends a document to Qdrant using a deterministic ID to avoid duplications.

    Args:
        client: Configured Qdrant client
        collection_name: Collection name
        text: Text to index
        metadata: Document metadata
        dry_run: If True, doesn't actually send to Qdrant

    Returns:
        Document ID or None if it fails
    """
    try:
        # Generate deterministic ID
        doc_id = generate_deterministic_id(
            metadata.get("project", "unknown"),
            metadata.get("absolute_path", "unknown"),
        )

        if dry_run:
            print(
                f"[DRY RUN] Generated ID: {doc_id} for: {metadata.get('absolute_path')}"
            )
            return doc_id

        # Use the upsert method to update if it exists or create if it doesn't
        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    payload=metadata,
                    vector={
                        "text": text,
                    },
                )
            ],
        )
        return doc_id
    except Exception as e:
        print(translate("cli.reindex.errors.qdrant_send_failed", error=str(e)))
        return None


def process_file(
    path: str,
    project_name: str,
    client: QdrantClient,
    collection_name: str,
    verbose: bool = False,
    dry_run: bool = False,
) -> Optional[int]:
    """
    Processes a single file and indexes it in Qdrant.

    Args:
        path: Path to the file
        project_name: Project name
        client: Qdrant client
        collection_name: Collection name
        verbose: If True, prints additional information
        dry_run: If True, doesn't actually send data to Qdrant

    Returns:
        ID of the indexed document or None if it fails
    """
    try:
        file_path = Path(path)
        if not file_path.is_file():
            if verbose:
                print(f"Ignoring: {path} (not a file)")
            return None

        # Check if it's a file we want to index
        # Ignore binary files, images, etc.
        ignored_extensions = {
            ".pyc",
            ".pyo",
            ".so",
            ".o",
            ".a",
            ".lib",
            ".dll",
            ".exe",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".flv",
            ".mkv",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
            ".7z",
        }

        if file_path.suffix.lower() in ignored_extensions:
            if verbose:
                print(f"Ignoring: {path} (ignored extension)")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            if verbose:
                print(f"Ignoring: {path} (binary file)")
            return None

        # Create metadata
        metadata = {
            "project": project_name,
            "absolute_path": str(file_path.absolute()),
            "extension": file_path.suffix.lstrip("."),
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
        }

        # Send to Qdrant
        if verbose:
            print(f"Processing: {path}")

        return send_to_qdrant(
            client=client,
            collection_name=collection_name,
            text=content,
            metadata=metadata,
            dry_run=dry_run,
        )
    except Exception as e:
        print(
            translate(
                "cli.reindex.errors.file_processing_error", path=path, error=str(e)
            )
        )
        return None


def process_directory(
    directory: str,
    project_name: str,
    client: QdrantClient,
    collection_name: str,
    verbose: bool = False,
    dry_run: bool = False,
) -> List[Union[int, None]]:
    """
    Recursively processes all files in a directory.

    Args:
        directory: Path to the directory
        project_name: Project name
        client: Qdrant client
        collection_name: Collection name
        verbose: If True, prints additional information
        dry_run: If True, doesn't actually send to Qdrant

    Returns:
        List of processed document IDs
    """
    results = []

    # Directories to ignore
    ignored_directories = {
        ".git",
        "__pycache__",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
    }

    for root, dirs, files in os.walk(directory):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignored_directories]

        for file in files:
            file_path = os.path.join(root, file)
            result = process_file(
                path=file_path,
                project_name=project_name,
                client=client,
                collection_name=collection_name,
                verbose=verbose,
                dry_run=dry_run,
            )
            results.append(result)

    return results


def main():
    """Main function of the reindexing script."""
    # Configure language from environment variable
    lang_code = os.environ.get("SYNAPSTOR_LANGUAGE", "en")
    if lang_code == "pt":
        set_language(Language.PORTUGUESE)
    else:
        set_language(Language.ENGLISH)

    parser = argparse.ArgumentParser(description=translate("cli.reindex.description"))

    parser.add_argument(
        "--project",
        "-p",
        required=True,
        help=translate("cli.reindex.project_help"),
    )

    parser.add_argument(
        "--path", required=True, help=translate("cli.reindex.path_help")
    )

    parser.add_argument(
        "--collection",
        "-c",
        default=os.environ.get("QDRANT_COLLECTION", "documents"),
        help=translate("cli.reindex.collection_help"),
    )

    parser.add_argument(
        "--url",
        default=os.environ.get("QDRANT_URL", "http://localhost:6333"),
        help=translate("cli.reindex.url_help"),
    )

    parser.add_argument(
        "--api-key",
        default=os.environ.get("QDRANT_API_KEY", ""),
        help=translate("cli.reindex.api_key_help"),
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=translate("cli.reindex.verbose_help"),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=translate("cli.reindex.dry_run_help"),
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Check if the collection was specified
    if not args.collection:
        print(translate("cli.reindex.errors.collection_not_provided"))
        parser.print_help()
        sys.exit(1)

    # Check if the path exists
    if not os.path.exists(args.path):
        print(translate("cli.reindex.errors.path_not_found", path=args.path))
        sys.exit(1)

    # Configure Qdrant client
    try:
        client_params = {
            "url": args.url,
        }

        if args.api_key:
            client_params["api_key"] = args.api_key

        client = QdrantClient(**client_params)

        # Check if the client is connected
        client.get_collections()

        if args.verbose:
            print(translate("cli.reindex.messages.connected_to_qdrant", url=args.url))

    except Exception as e:
        print(translate("cli.reindex.errors.qdrant_connection_failed", error=str(e)))
        sys.exit(1)

    # Check if the collection exists
    try:
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]

        if args.collection not in collection_names:
            print(
                translate(
                    "cli.reindex.warnings.collection_not_exists",
                    collection=args.collection,
                )
            )

            if not args.dry_run:
                create = (
                    input(translate("cli.reindex.prompts.create_collection")).lower()
                    == "y"
                )
                if create:
                    # Create collection with basic configuration
                    client.create_collection(
                        collection_name=args.collection,
                        vectors_config={
                            "text": models.VectorParams(
                                size=384,  # Typical dimension for embeddings
                                distance=models.Distance.COSINE,
                            )
                        },
                    )
                    print(
                        translate(
                            "cli.reindex.messages.collection_created",
                            collection=args.collection,
                        )
                    )
                else:
                    print(translate("cli.reindex.messages.operation_cancelled"))
                    sys.exit(0)
    except Exception as e:
        print(translate("cli.reindex.errors.collection_check_failed", error=str(e)))
        if not args.dry_run:
            sys.exit(1)

    # Process the path
    try:
        if os.path.isfile(args.path):
            if args.verbose:
                print(translate("cli.reindex.messages.processing_file", path=args.path))

            result = process_file(
                path=args.path,
                project_name=args.project,
                client=client,
                collection_name=args.collection,
                verbose=args.verbose,
                dry_run=args.dry_run,
            )

            if result:
                print(
                    translate(
                        "cli.reindex.messages.file_processed_successfully", id=result
                    )
                )
            else:
                print(translate("cli.reindex.messages.file_processing_failed"))

        elif os.path.isdir(args.path):
            if args.verbose:
                print(
                    translate(
                        "cli.reindex.messages.processing_directory", path=args.path
                    )
                )

            results = process_directory(
                directory=args.path,
                project_name=args.project,
                client=client,
                collection_name=args.collection,
                verbose=args.verbose,
                dry_run=args.dry_run,
            )

            # Count successful results
            success = [r for r in results if r is not None]
            print(
                translate(
                    "cli.reindex.messages.processing_completed",
                    success=len(success),
                    total=len(results),
                )
            )

        else:
            print(translate("cli.reindex.errors.invalid_path", path=args.path))
            sys.exit(1)

    except Exception as e:
        print(translate("cli.reindex.errors.processing_failed", error=str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
