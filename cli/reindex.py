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
            metadata.get("projeto", "unknown"),
            metadata.get("caminho_absoluto", "unknown"),
        )

        if dry_run:
            print(
                f"[DRY RUN] Generated ID: {doc_id} for: {metadata.get('caminho_absoluto')}"
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
        print(f"Error sending to Qdrant: {str(e)}")
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
            "projeto": project_name,
            "caminho_absoluto": str(file_path.absolute()),
            "extensao": file_path.suffix.lstrip("."),
            "nome_arquivo": file_path.name,
            "tamanho_bytes": file_path.stat().st_size,
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
        print(f"Error processing file {path}: {str(e)}")
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
    parser = argparse.ArgumentParser(
        description="Reindex content in Qdrant without duplication"
    )

    parser.add_argument(
        "--project",
        "-p",
        required=True,
        help="Project name for document identification",
    )

    parser.add_argument(
        "--path", required=True, help="Path to file or directory to be indexed"
    )

    parser.add_argument(
        "--collection",
        "-c",
        default=os.environ.get("QDRANT_COLLECTION", "documents"),
        help="Name of the collection in Qdrant (default env: QDRANT_COLLECTION or 'documents')",
    )

    parser.add_argument(
        "--url",
        default=os.environ.get("QDRANT_URL", "http://localhost:6333"),
        help="Qdrant server URL (default env: QDRANT_URL or 'http://localhost:6333')",
    )

    parser.add_argument(
        "--api-key",
        default=os.environ.get("QDRANT_API_KEY", ""),
        help="API key for Qdrant (default env: QDRANT_API_KEY)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show additional information during processing",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executes without sending data to Qdrant (only simulates)",
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Check if the collection was specified
    if not args.collection:
        print("Error: Collection name not provided")
        parser.print_help()
        sys.exit(1)

    # Check if the path exists
    if not os.path.exists(args.path):
        print(f"Error: Path not found: {args.path}")
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
            print(f"Connected to Qdrant at {args.url}")

    except Exception as e:
        print(f"Error connecting to Qdrant: {str(e)}")
        sys.exit(1)

    # Check if the collection exists
    try:
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]

        if args.collection not in collection_names:
            print(f"Warning: Collection '{args.collection}' does not exist.")

            if not args.dry_run:
                create = (
                    input("Do you want to create the collection? (y/n): ").lower()
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
                    print(f"Collection '{args.collection}' created successfully.")
                else:
                    print("Operation cancelled.")
                    sys.exit(0)
    except Exception as e:
        print(f"Error checking collections: {str(e)}")
        if not args.dry_run:
            sys.exit(1)

    # Process the path
    try:
        if os.path.isfile(args.path):
            if args.verbose:
                print(f"Processing file: {args.path}")

            result = process_file(
                path=args.path,
                project_name=args.project,
                client=client,
                collection_name=args.collection,
                verbose=args.verbose,
                dry_run=args.dry_run,
            )

            if result:
                print(f"File processed successfully. ID: {result}")
            else:
                print("Failed to process file.")

        elif os.path.isdir(args.path):
            if args.verbose:
                print(f"Processing directory: {args.path}")

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
                f"Processing completed. {len(success)} of {len(results)} files indexed."
            )

        else:
            print(f"Error: Specified path is not valid: {args.path}")
            sys.exit(1)

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
