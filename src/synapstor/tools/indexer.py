#!/usr/bin/env python3
"""
Indexer is a tool for indexing entire projects at once.

This script directly indexes files in Qdrant Cloud, without MCP Server dependencies.
It uses the official Qdrant Python client directly.

Usage:
    python indexer.py --project <project_name> --path <project_path>
    [--collection <collection_name>]

Example:
    python indexer.py --project my-project --path "/path/to/project"
"""

import argparse
import os
import sys
from pathlib import Path
import time
from typing import Dict, List, Any, Optional
import concurrent.futures
import logging
import hashlib
from tqdm import tqdm
from src.synapstor.i18n import _
from qdrant_client import models
import pathspec


# Logging configuration - DISABLES LOGS by default
# This prevents messages from appearing during normal execution
logging.basicConfig(level=logging.CRITICAL)  # Only shows critical errors
logger = logging.getLogger("indexer")

# Try to import the deterministic ID generation module and MEF support
try:
    from src.synapstor.utils.id_generator import generate_deterministic_id

    print("✅", _("indexer.using_deterministic_id"))
except ImportError:
    # Fallback function if the module doesn't exist
    def generate_deterministic_id(metadata: Dict[str, Any]) -> str:
        """Internal fallback version of the deterministic ID generator"""
        # Extract identification data
        project = metadata.get("project", "") or metadata.get("projeto", "")
        absolute_path = metadata.get("absolute_path", "") or metadata.get(
            "caminho_absoluto", ""
        )

        # If there's no project and path, try to use other identifiers
        if not (project and absolute_path):
            content_hash = ""
            # Try to use filename if available
            filename = metadata.get("filename", "") or metadata.get("nome_arquivo", "")
            if filename:
                content_hash += f"file:{filename};"

            # Use any available metadata to create a unique string
            for key in sorted(metadata.keys()):
                if key not in [
                    "project",
                    "projeto",
                    "absolute_path",
                    "caminho_absoluto",
                    "filename",
                    "nome_arquivo",
                ]:
                    value = str(metadata[key])
                    if value:
                        content_hash += f"{key}:{value};"
        else:
            # Use the project+absolute_path combination as the main identifier
            content_hash = f"{project}:{absolute_path}"

        # If there's still nothing for hash, raise an error
        if not content_hash:
            print("❌", _("indexer.insufficient_metadata_error"), metadata)
            raise ValueError(_("indexer.insufficient_metadata_error"))

        # Calculate MD5 hash of the identification string
        return hashlib.md5(content_hash.encode("utf-8")).hexdigest()

    print("⚠️", _("indexer.fallback_id_generator"))

# Try to import MEF support
try:
    from src.synapstor.mef import MEFParser

    MEF_AVAILABLE = True
    print("✅", _("indexer.mef_support_available"))
except ImportError:
    MEF_AVAILABLE = False
    print("⚠️", _("indexer.mef_support_unavailable"))


class ConsolePrinter:
    """A class that handles console output with verbose mode control.

    This class provides methods to print messages conditionally based on a
    verbose flag, allowing for controlled debug/info output while ensuring
    errors are always displayed.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def print(self, *args, **kwargs):
        """Only prints if in verbose mode"""
        if self.verbose:
            print(*args, **kwargs)

    def error(self, *args, **kwargs):
        """Always prints errors"""
        print(*args, **kwargs)


# Global instance that will be configured in main
console = ConsolePrinter()


# Silent function to load .env
def load_dotenv_file():
    try:
        from dotenv import load_dotenv

        load_dotenv()
        return True
    except ImportError:
        return False


# Backward compatibility alias
carregar_dotenv = load_dotenv_file


# Silently checks dependencies
def verificar_dependencias():
    """Checks necessary dependencies and installs them if not present"""
    deps = {
        "qdrant-client": "qdrant_client",
        "sentence-transformers": "sentence_transformers",
        "pathspec": "pathspec",
        "tqdm": "tqdm",
    }

    missing = []
    for pkg_name, import_name in deps.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        print(f"Installing dependencies: {', '.join(missing)}")
        import subprocess

        for pkg in missing:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"Error installing {pkg}: {e}")
                if pkg in ["qdrant-client", "tqdm"]:
                    sys.exit(1)
        print("Dependencies successfully installed!")


# Silently imports libraries
def importar_bibliotecas():
    try:

        return True
    except ImportError as e:
        print(f"Error importing dependencies: {e}")
        sys.exit(1)


# Early global import
try:
    import pathspec
except ImportError:
    pass  # Will be handled by verificar_dependencias

# Default patterns to ignore (similar to .gitignore)
DEFAULT_IGNORE_PATTERNS = [
    ".git/",
    "node_modules/",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "build/",
    "dist/",
    "*.egg-info/",
    ".env",
    "venv/",
    ".venv/",
    ".mypy_cache/",
    ".pytest_cache/",
    ".idea/",
    ".vscode/",
    "*.swp",
    "*.swo",
]

# Known binary file extensions
BINARY_EXTENSIONS = {
    # Images
    "png",
    "jpg",
    "jpeg",
    "gif",
    "bmp",
    "tiff",
    "webp",
    "ico",
    "svg",
    # Audio/Video
    "mp3",
    "wav",
    "ogg",
    "mp4",
    "avi",
    "mov",
    "mkv",
    "flv",
    "webm",
    # Compiled documents
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    # Compressed files
    "zip",
    "tar",
    "gz",
    "rar",
    "7z",
    "jar",
    "war",
    # Binaries
    "exe",
    "dll",
    "so",
    "class",
    "pyc",
    "pyo",
    "o",
    "a",
    "lib",
    "bin",
    # Others
    "dat",
    "db",
    "sqlite",
    "sqlite3",
}


class GitIgnoreFilter:
    """Filters files based on .gitignore rules"""

    def __init__(self, project_path: Path):
        """Initializes the filter with the project path"""
        self.project_path = project_path

        # Load patterns from .gitignore if available
        self.patterns = self._load_gitignore(project_path)

    def _load_gitignore(self, project_path: Path) -> List[str]:
        """Loads the .gitignore file using pathspec"""
        gitignore_path = project_path / ".gitignore"
        patterns = []

        # Add default patterns
        patterns.extend(DEFAULT_IGNORE_PATTERNS)

        # Add patterns from local .gitignore, if it exists
        if gitignore_path.exists():
            print(f"✅ Using configurations from .gitignore file: {gitignore_path}")
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    gitignore_content = f.read()

                # Add each non-empty line that isn't a comment
                for line in gitignore_content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
            except Exception as e:
                print(f"⚠️ Error reading .gitignore: {e}")
        else:
            print("ℹ️ .gitignore file not found, using default patterns.")

        return patterns

    def should_ignore(self, path: Path) -> bool:
        """Checks if a path should be ignored according to the rules"""
        try:
            # Convert to a path relative to the project
            rel_path = path.relative_to(self.project_path)
            str_path = str(rel_path).replace(os.sep, "/")

            # Use pathspec to check if the file should be ignored
            spec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, self.patterns
            )
            return spec.match_file(str_path)
        except ValueError:
            # If the path is not relative to the project, don't ignore
            return False
        except Exception as e:
            print(f"⚠️ Error checking ignore rules for {path}: {e}")
            return True  # For safety, ignore in case of error


class DirectIndexer:
    """Class for directly indexing projects in Qdrant Cloud"""

    def __init__(
        self,
        project_name: str,
        project_path: str,
        collection_name: str = "synapstor",
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        max_workers: int = 4,
        batch_size: int = 10,
        max_file_size: int = 5 * 1024 * 1024,  # 5MB by default
        vector_name: str = "fast-all-MiniLM-L6-v2",  # Default vector name
        mef_enabled: bool = False,  # Enable MEF processing
        mef_enforce_structure: bool = False,  # Enforce MEF structure validation
    ):
        # Validate and configure paths
        self.project_name = project_name
        self.project_path = Path(project_path)
        self.collection_name = collection_name
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.max_file_size = max_file_size
        self.vector_name = vector_name
        self.verbose = console.verbose  # Add the verbose attribute
        self.mef_enabled = mef_enabled and MEF_AVAILABLE
        self.mef_enforce_structure = mef_enforce_structure

        # Initialize MEF parser if enabled
        self.mef_parser = None
        if self.mef_enabled:
            try:
                self.mef_parser = MEFParser(enforce_structure=mef_enforce_structure)
                print(
                    "✅",
                    _("indexer.mef_processing"),
                    f"(enforce_structure={mef_enforce_structure})",
                )
            except (ImportError, ValueError, TypeError) as e:
                print(f"⚠️ Failed to initialize MEF parser: {e}")
                self.mef_enabled = False

        # Initialize Qdrant client
        try:
            from qdrant_client import QdrantClient

            # Get URL and API key from .env if not provided
            if not qdrant_url:
                qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:6333")

            if not qdrant_api_key:
                qdrant_api_key = os.environ.get("QDRANT_API_KEY", None)

            # Initialize the client
            if qdrant_api_key:
                self.qdrant_client = QdrantClient(
                    url=qdrant_url, api_key=qdrant_api_key
                )
            else:
                self.qdrant_client = QdrantClient(url=qdrant_url)

            print(f"✅ Connected to Qdrant server: {qdrant_url}")
        except Exception as e:
            print(f"❌ Failed to connect to Qdrant: {e}")
            raise ValueError(f"Could not connect to Qdrant server: {e}")

        # Initialize the embeddings model
        try:
            from sentence_transformers import SentenceTransformer

            print(f"🧠 Loading embeddings model: {embedding_model}")
            self.embedding_model = SentenceTransformer(embedding_model)
            print("✅ Embeddings model successfully loaded")
        except Exception as e:
            print(f"❌ Failed to load embeddings model: {e}")
            raise ValueError(f"Could not load the embeddings model: {e}") from e

        # Initialize the file filter based on .gitignore
        self.gitignore_filter = GitIgnoreFilter(self.project_path)

        # Statistics
        self.indexed_files = 0
        self.ignored_files = 0
        self.error_files = 0
        self.total_size = 0

        # Check if the directory exists
        if not self.project_path.exists() or not self.project_path.is_dir():
            raise ValueError(
                f"The project path does not exist or is not a directory: "
                f"{project_path}"
            )

        # Ensure the collection exists
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensures the collection exists in Qdrant, creating it if necessary"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_exists = any(
                col.name == self.collection_name for col in collections
            )

            if not collection_exists:
                print(f"🔍 Creating collection: {self.collection_name}")

                # Get the embedding dimension from the model
                vector_size = self.embedding_model.get_sentence_embedding_dimension()

                # Create the collection with the correctly named vector
                vector_config = {
                    self.vector_name: models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    )
                }

                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=vector_config,
                )
                print(
                    f"✅ Collection '{self.collection_name}' successfully created "
                    f"using vector name '{self.vector_name}'!"
                )
            else:
                print(f"✅ Collection '{self.collection_name}' already exists.")
                # Get the collection configuration to get the vector name
                self._obter_configuracao_colecao()
        except (ValueError, ConnectionError, RuntimeError) as e:
            print(f"❌ Error checking or creating collection: {e}")
            raise ValueError(f"Could not check or create the collection: {e}")

    def _obter_configuracao_colecao(self):
        """Gets the existing collection configuration to determine the vector name"""
        try:
            # Get the collection configuration
            colecao_info = self.qdrant_client.get_collection(self.collection_name)

            # Detailed debug information about the collection
            if logging.getLogger().level <= logging.DEBUG:
                self._imprimir_info_colecao(colecao_info)

            # Check if there's vector configuration
            if (
                hasattr(colecao_info, "config")
                and hasattr(colecao_info.config, "params")
                and hasattr(colecao_info.config.params, "vectors")
            ):
                # If the configuration has multiple vectors, get the first one
                vector_config = colecao_info.config.params.vectors
                if isinstance(vector_config, dict) and vector_config:
                    # Get the first vector name from the keys
                    self.vector_name = next(iter(vector_config.keys()))
                    print(f"✅ Using existing vector name: {self.vector_name}")
                    return

            # If can't determine, use the default
            self.vector_name = "fast-all-minilm-l6-v2"
            print(
                f"⚠️ Could not determine the vector name. "
                f"Using default: {self.vector_name}"
            )

        except (ValueError, ConnectionError, RuntimeError, AttributeError) as e:
            # In case of error, use the default
            self.vector_name = "fast-all-minilm-l6-v2"
            print(
                f"⚠️ Error getting collection configuration: {e}. "
                f"Using default vector name: {self.vector_name}"
            )

    def _imprimir_info_colecao(self, colecao_info):
        """Prints detailed information about the collection for debugging"""
        print("🔍 Detailed collection information:")

        try:
            # Basic information
            print(f"  Name: {colecao_info.name}")

            # Vector configuration
            if hasattr(colecao_info, "config") and hasattr(
                colecao_info.config, "params"
            ):
                print("  Vector configuration:")

                if hasattr(colecao_info.config.params, "vectors"):
                    vectors_config = colecao_info.config.params.vectors
                    if isinstance(vectors_config, dict):
                        for vector_name, vector_params in vectors_config.items():
                            size = getattr(vector_params, "size", "N/A")
                            distance = getattr(vector_params, "distance", "N/A")
                            print(
                                f"    - {vector_name}: size={size}, distance={distance}"
                            )
                    else:
                        print(f"    - Single vector configuration: {vectors_config}")
                else:
                    print("    No vector configuration found")

            # Point count
            if hasattr(colecao_info, "vectors_count"):
                print(f"  Total points: {colecao_info.vectors_count}")

            # Collection status
            if hasattr(colecao_info, "status"):
                print(f"  Status: {colecao_info.status}")

        except (ValueError, AttributeError, TypeError, OSError) as e:
            print(f"  Error printing detailed information: {e}")

    def _is_binary_file(self, file_path: Path) -> bool:
        """Checks if a file is binary through multiple heuristics"""
        # 1. Check by extension
        extension = file_path.suffix.lower()[1:] if file_path.suffix else ""
        if extension in BINARY_EXTENSIONS:
            return True

        # 2. Check by size (very large files are considered binary)
        try:
            if file_path.stat().st_size > self.max_file_size:
                return True
        except (OSError, PermissionError):
            return True  # In case of error checking size, assume binary

        # 3. Check by content
        try:
            if file_path.is_file():
                with open(file_path, "rb") as f:
                    chunk = f.read(4096)

                    # Empty file
                    if not chunk:
                        return False

                    # Presence of null bytes indicates binary file
                    if b"\x00" in chunk:
                        return True

                    # Another heuristic: high proportion of non-printable bytes
                    # Count non-ASCII or control bytes
                    non_text = sum(
                        1 for b in chunk if b < 9 or (b > 126 and b != 10 and b != 13)
                    )
                    if (
                        len(chunk) > 0
                        and non_text / len(chunk) > 0.3
                        and len(chunk) > 50
                    ):
                        return True
            return False
        except (OSError, PermissionError, UnicodeDecodeError):
            return True  # In case of error, assume binary for safety

    def should_ignore(self, file_path: Path) -> bool:
        """Decides if a file should be ignored, combining various checks"""
        # First check if it's a file
        if not file_path.is_file():
            return True

        # Check if the file is hidden (starts with .)
        if file_path.name.startswith("."):
            return True

        # Use the .gitignore filter
        if self.gitignore_filter.should_ignore(file_path):
            return True

        # Check if it's binary
        if self._is_binary_file(file_path):
            return True

        return False

    def _read_file(self, file_path: Path) -> Optional[str]:
        """Reads the content of a file with encoding handling"""
        # List of encodings to try
        encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                    # Check if it's not too large for embedding
                    if len(content) > 100000:  # Limit to ~100KB of text
                        content = content[:100000]
                    return content
            except UnicodeDecodeError:
                continue
            except IOError as e:
                print("⚠️", _("indexer.reading_error", file=file_path, error=e))
                return None

        # If all encodings fail
        return None

    def _get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extracts factual metadata from a file with MEF support"""
        # Path relative to the project
        try:
            relative_path = str(file_path.relative_to(self.project_path))
        except ValueError:
            relative_path = str(file_path)

        # File name and extension
        filename = file_path.name
        extension = (
            file_path.suffix[1:] if file_path.suffix else ""
        )  # Remove the initial dot

        # File information
        try:
            stats = os.stat(file_path)
            size_bytes = stats.st_size
            modification_date = time.strftime(
                "%Y-%m-%dT%H:%M:%S", time.localtime(stats.st_mtime)
            )
        except (OSError, PermissionError):
            size_bytes = 0
            modification_date = None

        # Create factual metadata needed for deterministic ID
        # Project and absolute_path are REQUIRED for a good ID
        metadata = {
            "project": self.project_name,
            "absolute_path": str(file_path.absolute()),
            "relative_path": relative_path,
            "filename": filename,
            "extension": extension,
            "size_bytes": size_bytes,
            # Backward compatibility
            "projeto": self.project_name,
            "caminho_absoluto": str(file_path.absolute()),
            "caminho_relativo": relative_path,
            "nome_arquivo": filename,
            "extensao": extension,
            "tamanho_bytes": size_bytes,
        }

        # Check for MEF processing
        if self.mef_enabled and self.mef_parser:
            try:
                mef_doc, mef_metadata = self.mef_parser.extract_mef_metadata(
                    file_path, self.project_name
                )
                # Convert MEF metadata to dict and merge
                mef_dict = mef_metadata.to_dict()
                metadata.update(mef_dict)

                if self.verbose and mef_metadata.is_mef_document:
                    print("📄", _("indexer.uki_processed", id=mef_metadata.mef_id))

            except (ValueError, TypeError, ImportError) as e:
                if self.verbose:
                    print(
                        "⚠️",
                        _("indexer.mef_validation_failed", file=relative_path, error=e),
                    )

        # Check if essential fields are present
        if not metadata["project"] or not metadata["absolute_path"]:
            print("⚠️", _("indexer.warning_incomplete_metadata", filename=filename))
            # Add a timestamp to at least ensure there's something unique
            metadata["timestamp"] = time.time()

        if modification_date:
            metadata["modification_date"] = modification_date
            metadata["data_modificacao"] = modification_date  # Backward compatibility

        return metadata

    def _send_to_qdrant(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Sends an entry directly to Qdrant"""
        try:
            # Local import to avoid type errors
            from qdrant_client import models

            # Create the text embedding
            embedding = self.embedding_model.encode(content)

            # Prepare the payload
            payload = {"document": content, "metadata": metadata}

            # Use the vector name determined at initialization
            vector_name = getattr(self, "vector_name", "vector")

            # Generate a deterministic ID based on metadata
            # This ensures the same file will always have the same ID
            try:
                deterministic_id = generate_deterministic_id(metadata)

                if self.verbose:
                    relative_path = metadata.get("relative_path", "") or metadata.get(
                        "caminho_relativo", "unknown"
                    )
                    print(f"🔑 ID generated for {relative_path}: {deterministic_id}")
            except Exception as e:
                print(f"❌ Error generating deterministic ID: {e}")
                print(f"⚠️ Metadata used: {metadata}")
                # Don't use UUID! Return failure
                return False

            # Create a point in Qdrant using deterministic ID
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=deterministic_id,  # Use deterministic ID
                        vector={vector_name: embedding},  # Use the vector name
                        payload=payload,
                    )
                ],
            )
            return True
        except Exception as e:
            print(f"❌ Error storing in Qdrant: {str(e)}")
            return False

    def _formatar_tamanho(self, tamanho_bytes: int) -> str:
        """Formats the size in bytes to a readable representation"""
        tamanho_formatado = float(tamanho_bytes)  # Explicitly convert to float
        for unit in ["B", "KB", "MB", "GB"]:
            if tamanho_formatado < 1024.0 or unit == "GB":
                break
            tamanho_formatado /= 1024.0
        return f"{tamanho_formatado:.2f} {unit}"

    def _process_file(self, file_path: Path) -> bool:
        """Processes a single file for indexing with MEF support"""
        try:
            rel_path = file_path.relative_to(self.project_path)

            # Skip if it should be ignored
            if self.should_ignore(file_path):
                # Don't log each ignored file to keep console clean
                return False

            # Get metadata first (includes MEF processing)
            metadata = self._get_metadata(file_path)

            # For MEF documents, use specialized content extraction
            if (
                self.mef_enabled
                and metadata.get("is_mef_document", False)
                and self.mef_parser
            ):
                try:
                    mef_doc, _MEF = self.mef_parser.extract_mef_metadata(
                        file_path, self.project_name
                    )
                    if mef_doc:
                        content = self.mef_parser.get_indexable_content(mef_doc)
                    else:
                        # Fallback to regular content reading
                        content = self._read_file(file_path)
                except (ValueError, TypeError, ImportError) as e:
                    if self.verbose:
                        print(
                            "⚠️",
                            _(
                                "indexer.content_extraction_failed",
                                file=rel_path,
                                error=e,
                            ),
                        )
                    content = self._read_file(file_path)
            else:
                # Regular content reading
                content = self._read_file(file_path)

            if content is None:
                # Only log errors, not files we can't read
                print("⚠️", _("indexer.failed_to_index", file=rel_path))
                return False

            # Check if the content is empty
            if not content.strip():
                return False

            # Send to Qdrant
            if self._send_to_qdrant(content, metadata):
                # Progress bar already shows indexing status
                return True
            else:
                print("❌", _("indexer.failed_to_index", file=rel_path))
                return False

        except (OSError, PermissionError, ValueError) as e:
            print("❌", _("indexer.file_error", file=file_path, error=e))
            return False

    def index(self) -> bool:
        """Indexes all files in the project recursively"""
        try:
            # Statistics
            total_files = 0
            files_to_process = []

            # Progress bar for file discovery
            print(f"🔍 Discovering files in: {self.project_path}")

            # Traverse all files recursively
            for root, _, files in os.walk(self.project_path):
                root_path = Path(root)
                for file in files:
                    total_files += 1
                    file_path = root_path / file
                    extension = file_path.suffix.lower()[1:] if file_path.suffix else ""

                    # Filter only text files that shouldn't be ignored by gitignore
                    if (
                        extension not in BINARY_EXTENSIONS
                        and not self.gitignore_filter.should_ignore(file_path)
                    ):
                        files_to_process.append(file_path)

            total_to_process = len(files_to_process)
            print(_("indexer.total_processing", total=total_to_process))

            # Reset counters
            self.indexed_files = 0
            self.ignored_files = 0

            # Main progress bar for indexing
            progress_format = (
                "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} "
                "[{elapsed}<{remaining}, {rate_fmt}]"
            )
            with tqdm(
                total=total_to_process,
                desc="Indexing",
                unit="file",
                bar_format=progress_format,
            ) as pbar:
                # Parallel processing (if applicable)
                if total_to_process > 20 and self.max_workers > 1:
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=self.max_workers
                    ) as executor:
                        # Define function for processing with progress
                        def process_with_progress(file_path):
                            rel_path = str(file_path.relative_to(self.project_path))
                            truncated_path = (
                                f"{rel_path[:40]}..."
                                if len(rel_path) > 40
                                else rel_path
                            )
                            pbar.set_description(f"Indexing: {truncated_path}")
                            result = self._process_file(file_path)
                            pbar.update(1)
                            return result

                        # Submit tasks
                        futures = []
                        for file_path in files_to_process:
                            futures.append(
                                executor.submit(process_with_progress, file_path)
                            )

                        # Collect results in real-time
                        indexed = 0
                        for i, future in enumerate(
                            concurrent.futures.as_completed(futures)
                        ):
                            result = future.result()
                            if result:
                                indexed += 1
                            # Update statistics in real-time
                            pbar.set_postfix(
                                indexed=f"{indexed}/{i + 1}",
                                rate=f"{(indexed / (i + 1)) * 100:.1f}%",
                            )

                        # Update final counters
                        self.indexed_files = indexed
                        self.ignored_files = total_to_process - indexed

                # Sequential processing
                else:
                    indexed = 0
                    for i, file_path in enumerate(files_to_process):
                        rel_path = str(file_path.relative_to(self.project_path))
                        truncated_path = (
                            f"{rel_path[:40]}..." if len(rel_path) > 40 else rel_path
                        )
                        pbar.set_description(f"Indexing: {truncated_path}")

                        if self._process_file(file_path):
                            indexed += 1

                        # Update statistics in real-time
                        pbar.set_postfix(
                            indexed=f"{indexed}/{i + 1}",
                            rate=f"{(indexed / (i + 1)) * 100:.1f}%",
                        )
                        pbar.update(1)

                # Update final counters
                self.indexed_files = indexed
                self.ignored_files = total_to_process - indexed

            # Clean and clear summary
            print("\n✅", _("indexer.indexing_completed"))
            print("📊", _("indexer.indexing_summary"))
            print(f"   Total files found: {total_files}")
            processable_pct = (total_to_process / total_files) * 100
            indexed_pct = (self.indexed_files / total_to_process) * 100
            print(f"   Processable files: {total_to_process} ({processable_pct:.1f}%)")
            print(
                "   ",
                _(
                    "indexer.indexed_files",
                    count=self.indexed_files,
                    percentage=indexed_pct,
                ),
            )

            return True

        except KeyboardInterrupt:
            print("\n⚠️ Indexing interrupted by user.")
            return False
        except (OSError, PermissionError, ValueError, RuntimeError) as e:
            print(f"\n❌ Error during indexing: {str(e)}")
            return False

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Searches for documents in Qdrant using a natural language query"""
        try:
            # Create the query embedding
            embedding = self.embedding_model.encode(query)

            # Search in Qdrant
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=limit,
            )

            # Format the results
            formatted_results = []
            for res in results:
                doc = res.payload.get("document", "")
                metadata = res.payload.get("metadata", {})
                score = res.score

                formatted_results.append(
                    {"document": doc, "metadata": metadata, "score": score}
                )

            return formatted_results
        except (ValueError, ConnectionError, RuntimeError) as e:
            print("❌", _("indexer.file_error", file="Qdrant", error=str(e)))
            return []

    # Backward compatibility alias
    def buscar(self, consulta: str, limite: int = 10) -> List[Dict[str, Any]]:
        """Backward compatibility method"""
        return self.search(consulta, limite)


def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(
        description="Indexer for Qdrant - Indexes projects for semantic search"
    )

    parser.add_argument(
        "--project",
        "-p",
        required=True,
        help="Project name (used as metadata for filtering)",
    )
    parser.add_argument(
        "--path",
        "-d",
        required=True,
        help="Path to the project directory to be indexed",
    )
    parser.add_argument(
        "--collection",
        "-c",
        default="synapstor",
        help="Collection name in Qdrant (default: synapstor)",
    )
    parser.add_argument(
        "--qdrant-url",
        help="Qdrant Cloud URL (by default, uses the QDRANT_URL value from .env)",
    )
    parser.add_argument(
        "--qdrant-api-key",
        help=(
            "Qdrant Cloud API Key (by default, uses the QDRANT_API_KEY value from .env)"
        ),
    )
    parser.add_argument(
        "--embedding-model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help=(
            "Embedding model to be used "
            "(default: sentence-transformers/all-MiniLM-L6-v2)"
        ),
    )
    parser.add_argument(
        "--vector-name",
        default=None,
        help=(
            "Vector name in the Qdrant collection "
            "(if not specified, will be detected automatically)"
        ),
    )
    parser.add_argument(
        "--query", "-q", help="Optional: performs a search after indexing"
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=4,
        help="Number of parallel workers for indexing (default: 4)",
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=5,
        help="Maximum file size in MB (default: 5)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose mode (shows more messages)",
    )
    parser.add_argument(
        "--recreate-collection",
        action="store_true",
        help="Recreates the collection if it already exists",
    )
    parser.add_argument(
        "--mef-enabled",
        "-m",
        action="store_true",
        help="Enable MEF (Matrix Embedding Framework) processing for YAML files",
    )
    parser.add_argument(
        "--mef-enforce-structure",
        "-e",
        action="store_true",
        help="Enforce strict MEF structure validation (requires --mef-enabled)",
    )

    args = parser.parse_args()

    # Configure verbose mode globally
    global console
    console = ConsolePrinter(verbose=args.verbose)

    # Prepare environment - silently
    carregar_dotenv()
    verificar_dependencias()

    try:
        # Create the indexer with minimalist interface and MEF support
        indexer = DirectIndexer(
            project_name=args.project,
            project_path=args.path,
            collection_name=args.collection,
            qdrant_url=args.qdrant_url,
            qdrant_api_key=args.qdrant_api_key,
            embedding_model=args.embedding_model,
            max_workers=args.workers,
            max_file_size=args.max_file_size * 1024 * 1024,
            vector_name=(
                "fast-all-minilm-l6-v2" if not args.vector_name else args.vector_name
            ),
            mef_enabled=args.mef_enabled,
            mef_enforce_structure=args.mef_enforce_structure,
        )

        # Run the indexing
        success = indexer.index()

        # If a query was provided, perform the search
        if args.query and success:
            print(f"\n🔍 Searching: '{args.query}'")
            results = indexer.search(args.query)

            if results:
                print(f"🔎 Found {len(results)} results:")
                for i, res in enumerate(results, 1):
                    print(f"\n--- Result {i} (Score: {res['score']:.4f}) ---")
                    metadata = res["metadata"]
                    relative_path = metadata.get("relative_path", "") or metadata.get(
                        "caminho_relativo", "Unknown"
                    )
                    print(f"📂 {relative_path}")

                    # Show a snippet of the document
                    doc = res["document"]
                    max_chars = 150
                    snippet = doc[:max_chars] + ("..." if len(doc) > max_chars else "")
                    print(f"📄 {snippet}")
            else:
                print("❓ No results found")

        return 0 if success else 1

    except (ValueError, OSError, ImportError, RuntimeError) as e:
        print(f"\n❌ Error: {e}")
        return 1


# Backward compatibility aliases
IndexadorDireto = DirectIndexer


if __name__ == "__main__":
    sys.exit(main())


def command_line_runner():
    """Entry point for the synapstor-index command."""
    sys.exit(main())
