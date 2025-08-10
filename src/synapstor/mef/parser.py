"""
Parser for Matrix Embedding Framework (MEF) documents.
"""

from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import yaml

from .types import MEFDocument, MEFMetadata, MEFExample


class MEFParser:
    """
    Parser for MEF YAML documents.

    Handles detection, parsing, and metadata extraction from MEF files.
    """

    def __init__(self, enforce_structure: bool = False):
        """
        Initialize MEF parser.

        Args:
            enforce_structure: If True, only accept strictly valid MEF documents
        """
        self.enforce_structure = enforce_structure

    def is_mef_document(self, file_path: Path) -> bool:
        """
        Check if a file is a MEF document.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file appears to be a MEF document
        """
        # Quick checks first
        if file_path.suffix.lower() not in [".yaml", ".yml"]:
            return False

        try:
            content = self._read_file(file_path)
            if not content:
                return False

            # Parse YAML
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                return False

            # Check for MEF identifier pattern
            mef_id = data.get("id", "")
            if not mef_id.startswith("unik-"):
                return False

            # Check for required MEF fields
            required_fields = ["title", "domain", "type", "content"]
            has_required = all(field in data for field in required_fields)

            return has_required

        except Exception:
            return False

    def parse_mef_document(self, file_path: Path) -> Optional[MEFDocument]:
        """
        Parse a MEF document from file.

        Args:
            file_path: Path to the MEF file

        Returns:
            Parsed MEF document or None if parsing fails
        """
        try:
            content = self._read_file(file_path)
            if not content:
                return None

            # Parse YAML
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                return None

            # Convert examples to proper format
            if "examples" in data and isinstance(data["examples"], list):
                examples = []
                for ex in data["examples"]:
                    if isinstance(ex, dict) and "input" in ex and "output" in ex:
                        examples.append(MEFExample(**ex))
                data["examples"] = examples

            # Handle date conversion
            if "last_validation" in data and isinstance(data["last_validation"], str):
                try:
                    # Try to parse date
                    date_obj = datetime.strptime(
                        data["last_validation"], "%Y-%m-%d"
                    ).date()
                    data["last_validation"] = date_obj
                except ValueError:
                    data["last_validation"] = None

            # Create MEF document
            mef_doc = MEFDocument(**data)
            return mef_doc

        except Exception as e:
            if self.enforce_structure:
                raise ValueError(f"Failed to parse MEF document {file_path}: {e}")
            return None

    def extract_mef_metadata(
        self, file_path: Path, project_name: str
    ) -> Tuple[Optional[MEFDocument], MEFMetadata]:
        """
        Extract MEF metadata from a file.

        Args:
            file_path: Path to the file
            project_name: Name of the project

        Returns:
            Tuple of (MEF document if applicable, enhanced metadata)
        """
        # Get basic file metadata
        metadata = self._get_base_metadata(file_path, project_name)

        # Check if it's a MEF document
        if self.is_mef_document(file_path):
            mef_doc = self.parse_mef_document(file_path)

            if mef_doc:
                # Enhance metadata with MEF information
                metadata.is_mef_document = True
                metadata.mef_id = mef_doc.id
                metadata.mef_domain = mef_doc.domain
                metadata.mef_type = mef_doc.type
                metadata.mef_context = mef_doc.context
                metadata.mef_language = mef_doc.language
                metadata.mef_intent_of_use = mef_doc.intent_of_use
                metadata.mef_use_case_stage = mef_doc.use_case_stage
                metadata.mef_related_to = mef_doc.related_to
                metadata.mef_examples_count = len(mef_doc.examples)

                if mef_doc.last_validation is not None:
                    metadata.mef_last_validation = mef_doc.last_validation.strftime(
                        "%Y-%m-%d"
                    )

                return mef_doc, metadata

        return None, metadata

    def get_indexable_content(self, mef_doc: MEFDocument) -> str:
        """
        Extract indexable content from MEF document.

        Args:
            mef_doc: Parsed MEF document

        Returns:
            Text content suitable for embedding
        """
        content_parts = []

        # Title and main content
        content_parts.append(f"Title: {mef_doc.title}")
        content_parts.append(f"Content: {mef_doc.content}")

        # Intent and use cases
        if mef_doc.intent_of_use:
            content_parts.append(f"Intent of use: {', '.join(mef_doc.intent_of_use)}")

        if mef_doc.use_case_stage:
            content_parts.append(
                f"Use case stages: {', '.join(mef_doc.use_case_stage)}"
            )

        # Examples
        if mef_doc.examples:
            examples_text = []
            for i, example in enumerate(mef_doc.examples, 1):
                examples_text.append(
                    f"Example {i}: Input: {example.input} -> Output: {example.output}"
                )
            content_parts.append("Examples: " + " | ".join(examples_text))

        # Domain and type context
        content_parts.append(
            f"Domain: {mef_doc.domain} | Type: {mef_doc.type} | Context: {mef_doc.context}"
        )

        return "\n\n".join(content_parts)

    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read file content with encoding handling."""
        encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                    if len(content) > 500000:  # 500KB limit for MEF files
                        content = content[:500000]
                    return content
            except (UnicodeDecodeError, IOError):
                continue

        return None

    def _get_base_metadata(self, file_path: Path, project_name: str) -> MEFMetadata:
        """Get base file metadata."""
        try:
            # Path relative to project (this will be set by caller)
            caminho_relativo = str(file_path)

            # File information
            stats = file_path.stat()
            tamanho_bytes = stats.st_size
            data_modificacao = datetime.fromtimestamp(stats.st_mtime).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )

            return MEFMetadata(
                projeto=project_name,
                caminho_absoluto=str(file_path.absolute()),
                caminho_relativo=caminho_relativo,
                nome_arquivo=file_path.name,
                extensao=file_path.suffix[1:] if file_path.suffix else "",
                tamanho_bytes=tamanho_bytes,
                data_modificacao=data_modificacao,
            )

        except (OSError, PermissionError, FileNotFoundError):
            # Return minimal metadata
            return MEFMetadata(
                projeto=project_name,
                caminho_absoluto=str(file_path.absolute()),
                caminho_relativo=str(file_path),
                nome_arquivo=file_path.name,
                extensao=file_path.suffix[1:] if file_path.suffix else "",
                tamanho_bytes=0,
            )
