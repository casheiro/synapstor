#!/usr/bin/env python3
"""
Indexer is a tool for indexing entire projects at once.

This script directly indexes files in Qdrant Cloud, without MCP Server dependencies.
It uses the official Qdrant Python client directly.

Usage:
    python indexer.py --project <project_name> --path <project_path> [--collection <collection_name>]

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
from tqdm import tqdm
import hashlib

# Logging configuration - DISABLES LOGS by default
# This prevents messages from appearing during normal execution
logging.basicConfig(level=logging.CRITICAL)  # Only shows critical errors
logger = logging.getLogger("indexer")

# Try to import the deterministic ID generation module
try:
    from synapstor.utils.id_generator import gerar_id_determinista

    print("✅ Using deterministic ID generator from synapstor.utils")
except ImportError:
    # Fallback function if the module doesn't exist
    def gerar_id_determinista(metadata: Dict[str, Any]) -> str:
        """Internal fallback version of the deterministic ID generator"""
        # Extract identification data
        projeto = metadata.get("projeto", "")
        caminho = metadata.get("caminho_absoluto", "")

        # If there's no project and path, try to use other identifiers
        if not (projeto and caminho):
            content_hash = ""
            # Try to use file_name if available
            if "nome_arquivo" in metadata:
                content_hash += f"file:{metadata['nome_arquivo']};"

            # Use any available metadata to create a unique string
            for key in sorted(metadata.keys()):
                if key not in ["projeto", "caminho_absoluto", "nome_arquivo"]:
                    value = str(metadata[key])
                    if value:
                        content_hash += f"{key}:{value};"
        else:
            # Use the project+absolute_path combination as the main identifier
            content_hash = f"{projeto}:{caminho}"

        # If there's still nothing for hash, raise an error
        if not content_hash:
            print("❌ Insufficient metadata to generate deterministic ID:", metadata)
            raise ValueError("Insufficient metadata to generate deterministic ID")

        # Calculate MD5 hash of the identification string
        return hashlib.md5(content_hash.encode("utf-8")).hexdigest()

    print(
        "⚠️\t Module synapstor.utils not found, using internal version of gerar_id_determinista"
    )


# Class to replace the print function with a version that only prints in verbose mode
class ConsolePrinter:
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
def carregar_dotenv():
    try:
        from dotenv import load_dotenv

        load_dotenv()
        return True
    except ImportError:
        return False


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
            except Exception as e:
                print(f"Error installing {pkg}: {e}")
                if pkg in ["qdrant-client", "tqdm"]:
                    sys.exit(1)
        print("Dependencies successfully installed!")


# Silently imports libraries
def importar_bibliotecas():
    try:
        global QdrantClient, models, SentenceTransformer, pathspec
        from qdrant_client import QdrantClient, models
        from sentence_transformers import SentenceTransformer
        import pathspec

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

    def __init__(self, projeto_path: Path):
        """Initializes the filter with the project path"""
        self.projeto_path = projeto_path

        # Load patterns from .gitignore if available
        self.patterns = self._carregar_gitignore(projeto_path)

    def _carregar_gitignore(self, projeto_path: Path) -> List[str]:
        """Loads the .gitignore file using pathspec"""
        gitignore_path = projeto_path / ".gitignore"
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

    def deve_ignorar(self, path: Path) -> bool:
        """Checks if a path should be ignored according to the rules"""
        try:
            # Convert to a path relative to the project
            rel_path = path.relative_to(self.projeto_path)
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


class IndexadorDireto:
    """Class for directly indexing projects in Qdrant Cloud"""

    def __init__(
        self,
        nome_projeto: str,
        caminho_projeto: str,
        collection_name: str = "synapstor",
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        max_workers: int = 4,
        tamanho_lote: int = 10,
        tamanho_maximo_arquivo: int = 5 * 1024 * 1024,  # 5MB by default
        vector_name: str = "fast-all-MiniLM-L6-v2",  # Default vector name
    ):
        # Validate and configure paths
        self.nome_projeto = nome_projeto
        self.caminho_projeto = Path(caminho_projeto)
        self.collection_name = collection_name
        self.max_workers = max_workers
        self.tamanho_lote = tamanho_lote
        self.tamanho_maximo_arquivo = tamanho_maximo_arquivo
        self.vector_name = vector_name
        self.verbose = console.verbose  # Add the verbose attribute

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
            raise ValueError(f"Could not load the embeddings model: {e}")

        # Initialize the file filter based on .gitignore
        self.gitignore_filter = GitIgnoreFilter(self.caminho_projeto)

        # Statistics
        self.arquivos_indexados = 0
        self.arquivos_ignorados = 0
        self.arquivos_com_erro = 0
        self.total_tamanho = 0

        # Check if the directory exists
        if not self.caminho_projeto.exists() or not self.caminho_projeto.is_dir():
            raise ValueError(
                f"The project path does not exist or is not a directory: {caminho_projeto}"
            )

        # Ensure the collection exists
        self._garantir_colecao()

    def _garantir_colecao(self):
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
                    f"✅ Collection '{self.collection_name}' successfully created using vector name '{self.vector_name}'!"
                )
            else:
                print(f"✅ Collection '{self.collection_name}' already exists.")
                # Get the collection configuration to get the vector name
                self._obter_configuracao_colecao()
        except Exception as e:
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
                f"⚠️ Could not determine the vector name. Using default: {self.vector_name}"
            )

        except Exception as e:
            # In case of error, use the default
            self.vector_name = "fast-all-minilm-l6-v2"
            print(
                f"⚠️ Error getting collection configuration: {e}. Using default vector name: {self.vector_name}"
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
                            print(
                                f"    - {vector_name}: size={getattr(vector_params, 'size', 'N/A')}, distance={getattr(vector_params, 'distance', 'N/A')}"
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

        except Exception as e:
            print(f"  Error printing detailed information: {e}")

    def _eh_arquivo_binario(self, caminho: Path) -> bool:
        """Checks if a file is binary through multiple heuristics"""
        # 1. Check by extension
        extensao = caminho.suffix.lower()[1:] if caminho.suffix else ""
        if extensao in BINARY_EXTENSIONS:
            return True

        # 2. Check by size (very large files are considered binary)
        try:
            if caminho.stat().st_size > self.tamanho_maximo_arquivo:
                return True
        except Exception:
            return True  # In case of error checking size, assume binary

        # 3. Check by content
        try:
            if caminho.is_file():
                with open(caminho, "rb") as f:
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
        except Exception:
            return True  # In case of error, assume binary for safety

    def deve_ignorar(self, caminho: Path) -> bool:
        """Decides if a file should be ignored, combining various checks"""
        # First check if it's a file
        if not caminho.is_file():
            return True

        # Check if the file is hidden (starts with .)
        if caminho.name.startswith("."):
            return True

        # Use the .gitignore filter
        if self.gitignore_filter.deve_ignorar(caminho):
            return True

        # Check if it's binary
        if self._eh_arquivo_binario(caminho):
            return True

        return False

    def _ler_arquivo(self, caminho: Path) -> Optional[str]:
        """Reads the content of a file with encoding handling"""
        # List of encodings to try
        encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                with open(caminho, "r", encoding=encoding) as f:
                    conteudo = f.read()
                    # Check if it's not too large for embedding
                    if len(conteudo) > 100000:  # Limit to ~100KB of text
                        conteudo = conteudo[:100000]
                    return conteudo
            except UnicodeDecodeError:
                continue
            except IOError as e:
                print(f"⚠️ Error reading {caminho}: {e}")
                return None

        # If all encodings fail
        return None

    def _obter_metadados(self, caminho: Path) -> Dict[str, Any]:
        """Extracts factual metadata from a file"""
        # Path relative to the project
        try:
            caminho_relativo = str(caminho.relative_to(self.caminho_projeto))
        except ValueError:
            caminho_relativo = str(caminho)

        # File name and extension
        nome_arquivo = caminho.name
        extensao = (
            caminho.suffix[1:] if caminho.suffix else ""
        )  # Remove the initial dot

        # File information
        try:
            stats = os.stat(caminho)
            tamanho_bytes = stats.st_size
            data_modificacao = time.strftime(
                "%Y-%m-%dT%H:%M:%S", time.localtime(stats.st_mtime)
            )
        except Exception:
            tamanho_bytes = 0
            data_modificacao = None

        # Create factual metadata needed for deterministic ID
        # Project and absolute_path are REQUIRED for a good ID
        metadata = {
            "projeto": self.nome_projeto,
            "caminho_absoluto": str(caminho.absolute()),
            "caminho_relativo": caminho_relativo,
            "nome_arquivo": nome_arquivo,
            "extensao": extensao,
            "tamanho_bytes": tamanho_bytes,
        }

        # Check if essential fields are present
        if not metadata["projeto"] or not metadata["caminho_absoluto"]:
            print(f"⚠️ Warning: Essential metadata incomplete for: {nome_arquivo}")
            # Add a timestamp to at least ensure there's something unique
            metadata["timestamp"] = time.time()

        if data_modificacao:
            metadata["data_modificacao"] = data_modificacao

        return metadata

    def _enviar_para_qdrant(self, conteudo: str, metadata: Dict[str, Any]) -> bool:
        """Sends an entry directly to Qdrant"""
        try:
            # Local import to avoid type errors
            from qdrant_client import models

            # Create the text embedding
            embedding = self.embedding_model.encode(conteudo)

            # Prepare the payload
            payload = {"document": conteudo, "metadata": metadata}

            # Use the vector name determined at initialization
            vector_name = getattr(self, "vector_name", "vector")

            # Generate a deterministic ID based on metadata
            # This ensures the same file will always have the same ID
            try:
                deterministic_id = gerar_id_determinista(metadata)

                if self.verbose:
                    caminho_rel = metadata.get("caminho_relativo", "unknown")
                    print(f"🔑 ID generated for {caminho_rel}: {deterministic_id}")
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

    def _processar_arquivo(self, caminho: Path) -> bool:
        """Processes a single file for indexing"""
        try:
            rel_path = caminho.relative_to(self.caminho_projeto)

            # Skip if it should be ignored
            if self.deve_ignorar(caminho):
                # Don't log each ignored file to keep console clean
                return False

            # Read file content
            conteudo = self._ler_arquivo(caminho)
            if conteudo is None:
                # Only log errors, not files we can't read
                print(f"⚠️ Could not read: {rel_path}")
                return False

            # Check if the content is empty
            if not conteudo.strip():
                return False

            # Get metadata
            metadados = self._obter_metadados(caminho)

            # Send to Qdrant
            if self._enviar_para_qdrant(conteudo, metadados):
                # We don't need to log each indexed file, the progress bar already shows it
                return True
            else:
                print(f"❌ Failed to index: {rel_path}")
                return False

        except Exception as e:
            print(f"❌ Error processing file {caminho}: {e}")
            return False

    def indexar(self) -> bool:
        """Indexes all files in the project recursively"""
        try:
            # Statistics
            total_arquivos = 0
            arquivos_para_processar = []

            # Progress bar for file discovery
            print(f"🔍 Discovering files in: {self.caminho_projeto}")

            # Traverse all files recursively
            for root, _, files in os.walk(self.caminho_projeto):
                root_path = Path(root)
                for file in files:
                    total_arquivos += 1
                    caminho = root_path / file
                    extensao = caminho.suffix.lower()[1:] if caminho.suffix else ""

                    # Filter only text files that shouldn't be ignored by gitignore
                    if (
                        extensao not in BINARY_EXTENSIONS
                        and not self.gitignore_filter.deve_ignorar(caminho)
                    ):
                        arquivos_para_processar.append(caminho)

            total_para_processar = len(arquivos_para_processar)
            print(f"Found {total_para_processar} processable files")

            # Reset counters
            self.arquivos_indexados = 0
            self.arquivos_ignorados = 0

            # Main progress bar for indexing
            with tqdm(
                total=total_para_processar,
                desc="Indexing",
                unit="file",
                bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            ) as pbar:

                # Parallel processing (if applicable)
                if total_para_processar > 20 and self.max_workers > 1:
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=self.max_workers
                    ) as executor:
                        # Define function for processing with progress
                        def processar_com_progresso(caminho):
                            rel_path = str(caminho.relative_to(self.caminho_projeto))
                            pbar.set_description(
                                f"Indexing: {rel_path[:40]}{'...' if len(rel_path) > 40 else ''}"
                            )
                            resultado = self._processar_arquivo(caminho)
                            pbar.update(1)
                            return resultado

                        # Submit tasks
                        futures = []
                        for caminho in arquivos_para_processar:
                            futures.append(
                                executor.submit(processar_com_progresso, caminho)
                            )

                        # Collect results in real-time
                        indexados = 0
                        for i, future in enumerate(
                            concurrent.futures.as_completed(futures)
                        ):
                            resultado = future.result()
                            if resultado:
                                indexados += 1
                            # Update statistics in real-time
                            pbar.set_postfix(
                                indexed=f"{indexados}/{i+1}",
                                rate=f"{(indexados/(i+1))*100:.1f}%",
                            )

                        # Update final counters
                        self.arquivos_indexados = indexados
                        self.arquivos_ignorados = total_para_processar - indexados

                # Sequential processing
                else:
                    indexados = 0
                    for i, caminho in enumerate(arquivos_para_processar):
                        rel_path = str(caminho.relative_to(self.caminho_projeto))
                        pbar.set_description(
                            f"Indexing: {rel_path[:40]}{'...' if len(rel_path) > 40 else ''}"
                        )

                        if self._processar_arquivo(caminho):
                            indexados += 1

                        # Update statistics in real-time
                        pbar.set_postfix(
                            indexed=f"{indexados}/{i+1}",
                            rate=f"{(indexados/(i+1))*100:.1f}%",
                        )
                        pbar.update(1)

                # Update final counters
                self.arquivos_indexados = indexados
                self.arquivos_ignorados = total_para_processar - indexados

            # Clean and clear summary
            print("\n✅ Indexing completed!")
            print("📊 Statistics:")
            print(f"   Total files found: {total_arquivos}")
            print(
                f"   Processable files: {total_para_processar} ({(total_para_processar/total_arquivos)*100:.1f}%)"
            )
            print(
                f"   Indexed files: {self.arquivos_indexados} ({(self.arquivos_indexados/total_para_processar)*100:.1f}%)"
            )

            return True

        except KeyboardInterrupt:
            print("\n⚠️ Indexing interrupted by user.")
            return False
        except Exception as e:
            print(f"\n❌ Error during indexing: {str(e)}")
            return False

    def buscar(self, consulta: str, limite: int = 10) -> List[Dict[str, Any]]:
        """Searches for documents in Qdrant using a natural language query"""
        try:
            # Create the query embedding
            embedding = self.embedding_model.encode(consulta)

            # Search in Qdrant
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=limite,
            )

            # Format the results
            resultados_formatados = []
            for res in results:
                doc = res.payload.get("document", "")
                metadata = res.payload.get("metadata", {})
                score = res.score

                resultados_formatados.append(
                    {"documento": doc, "metadata": metadata, "score": score}
                )

            return resultados_formatados
        except Exception as e:
            print(f"❌ Error searching in Qdrant: {str(e)}")
            return []


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
        help="Qdrant Cloud API Key (by default, uses the QDRANT_API_KEY value from .env)",
    )
    parser.add_argument(
        "--embedding-model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model to be used (default: sentence-transformers/all-MiniLM-L6-v2)",
    )
    parser.add_argument(
        "--vector-name",
        default=None,
        help="Vector name in the Qdrant collection (if not specified, will be detected automatically)",
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

    args = parser.parse_args()

    # Configure verbose mode globally
    global console
    console = ConsolePrinter(verbose=args.verbose)

    # Prepare environment - silently
    carregar_dotenv()
    verificar_dependencias()
    importar_bibliotecas()

    try:
        # Create the indexer with minimalist interface
        indexador = IndexadorDireto(
            nome_projeto=args.project,
            caminho_projeto=args.path,
            collection_name=args.collection,
            qdrant_url=args.qdrant_url,
            qdrant_api_key=args.qdrant_api_key,
            embedding_model=args.embedding_model,
            max_workers=args.workers,
            tamanho_maximo_arquivo=args.max_file_size * 1024 * 1024,
            vector_name=(
                "fast-all-minilm-l6-v2" if not args.vector_name else args.vector_name
            ),
        )

        # Run the indexing
        success = indexador.indexar()

        # If a query was provided, perform the search
        if args.query and success:
            print(f"\n🔍 Searching: '{args.query}'")
            resultados = indexador.buscar(args.query)

            if resultados:
                print(f"🔎 Found {len(resultados)} results:")
                for i, res in enumerate(resultados, 1):
                    print(f"\n--- Result {i} (Score: {res['score']:.4f}) ---")
                    metadata = res["metadata"]
                    print(f"📂 {metadata.get('caminho_relativo', 'Unknown')}")

                    # Show a snippet of the document
                    doc = res["documento"]
                    max_chars = 150
                    trecho = doc[:max_chars] + ("..." if len(doc) > max_chars else "")
                    print(f"📄 {trecho}")
            else:
                print("❓ No results found")

        return 0 if success else 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


def command_line_runner():
    """Entry point for the synapstor-index command."""
    sys.exit(main())
