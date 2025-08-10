"""
Validator for Matrix Embedding Framework (MEF) documents.
"""

from typing import List, Dict, Any
from pathlib import Path

from .parser import MEFParser
from .types import MEFDocument


class MEFValidationError(Exception):
    """Exception raised for MEF validation errors."""

    pass


class MEFValidator:
    """
    Validator for MEF documents.

    Provides validation capabilities for MEF structure and content.
    """

    def __init__(
        self,
        supported_domains: List[str] = None,
        supported_types: List[str] = None,
        supported_contexts: List[str] = None,
        required_fields: List[str] = None,
    ):
        """
        Initialize MEF validator.

        Args:
            supported_domains: List of valid domains
            supported_types: List of valid types
            supported_contexts: List of valid contexts
            required_fields: List of required fields
        """
        self.supported_domains = supported_domains or [
            "product",
            "business",
            "technical",
            "strategy",
            "culture",
        ]
        self.supported_types = supported_types or [
            "business_rule",
            "function",
            "template",
            "guideline",
            "pattern",
            "decision",
            "example",
        ]
        self.supported_contexts = supported_contexts or [
            "discovery",
            "implementation",
            "refinement",
            "qa",
            "documentation",
            "support",
        ]
        self.required_fields = required_fields or [
            "id",
            "title",
            "domain",
            "type",
            "content",
        ]

    def validate_document(self, mef_doc: MEFDocument) -> List[str]:
        """
        Validate a MEF document.

        Args:
            mef_doc: MEF document to validate

        Returns:
            List of validation warnings (empty if valid)
        """
        warnings: List[str] = []

        # Validate ID format
        if not self._validate_id_format(mef_doc.id):
            warnings.append(f"Invalid ID format: {mef_doc.id}")

        # Validate domain
        if mef_doc.domain not in self.supported_domains:
            warnings.append(f"Unsupported domain: {mef_doc.domain}")

        # Validate type
        if mef_doc.type not in self.supported_types:
            warnings.append(f"Unsupported type: {mef_doc.type}")

        # Validate context
        if mef_doc.context not in self.supported_contexts:
            warnings.append(f"Unsupported context: {mef_doc.context}")

        # Validate content quality
        content_warnings = self._validate_content_quality(mef_doc)
        warnings.extend(content_warnings)

        # Validate relationships
        relationship_warnings = self._validate_relationships(mef_doc)
        warnings.extend(relationship_warnings)

        return warnings

    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a MEF file.

        Args:
            file_path: Path to the file to validate

        Returns:
            Validation result with status and details
        """
        result: Dict[str, Any] = {
            "is_mef": False,
            "is_valid": False,
            "warnings": [],
            "errors": [],
        }

        try:
            parser = MEFParser(enforce_structure=True)

            # Check if it's a MEF document
            if not parser.is_mef_document(file_path):
                result["errors"].append("Not a valid MEF document")
                return result

            result["is_mef"] = True

            # Parse document
            mef_doc = parser.parse_mef_document(file_path)
            if not mef_doc:
                result["errors"].append("Failed to parse MEF document")
                return result

            # Validate document
            warnings = self.validate_document(mef_doc)
            result["warnings"] = warnings
            result["is_valid"] = len(warnings) == 0

            # Add document info
            result["document_info"] = {
                "id": mef_doc.id,
                "title": mef_doc.title,
                "domain": mef_doc.domain,
                "type": mef_doc.type,
                "context": mef_doc.context,
            }

        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")

        return result

    def _validate_id_format(self, mef_id: str) -> bool:
        """Validate MEF ID format."""
        if not mef_id.startswith("unik-"):
            return False

        parts = mef_id.split("-")
        if len(parts) < 3:
            return False

        # Domain should be valid
        if len(parts) > 2 and parts[1] not in self.supported_domains:
            return False

        return True

    def _validate_content_quality(self, mef_doc: MEFDocument) -> List[str]:
        """Validate content quality."""
        warnings: List[str] = []

        # Check content length
        if len(mef_doc.content.strip()) < 50:
            warnings.append("Content is too short (minimum 50 characters)")

        # Check title quality
        if len(mef_doc.title.strip()) < 5:
            warnings.append("Title is too short")

        if len(mef_doc.title) > 100:
            warnings.append("Title is too long (maximum 100 characters)")

        # Check examples quality
        if mef_doc.examples:
            for i, example in enumerate(mef_doc.examples):
                if not example.input.strip() or not example.output.strip():
                    warnings.append(f"Example {i+1} has empty input or output")

        # Check intent and use cases
        if not mef_doc.intent_of_use:
            warnings.append("No intent_of_use specified")

        if not mef_doc.use_case_stage:
            warnings.append("No use_case_stage specified")

        return warnings

    def _validate_relationships(self, mef_doc: MEFDocument) -> List[str]:
        """Validate relationships."""
        warnings: List[str] = []

        # Check related_to format
        for related_id in mef_doc.related_to:
            if not self._validate_id_format(related_id):
                warnings.append(f"Invalid related ID format: {related_id}")

        return warnings

    def get_validation_summary(self, directory: Path) -> Dict[str, Any]:
        """
        Get validation summary for all MEF files in a directory.

        Args:
            directory: Directory to scan for MEF files

        Returns:
            Validation summary
        """
        summary: Dict[str, Any] = {
            "total_files": 0,
            "mef_files": 0,
            "valid_files": 0,
            "files_with_warnings": 0,
            "files_with_errors": 0,
            "details": [],
        }

        # Find all YAML files
        yaml_files = list(directory.rglob("*.yaml")) + list(directory.rglob("*.yml"))

        for yaml_file in yaml_files:
            summary["total_files"] += 1

            result = self.validate_file(yaml_file)

            if result["is_mef"]:
                summary["mef_files"] += 1

                if result["is_valid"]:
                    summary["valid_files"] += 1

                if result["warnings"]:
                    summary["files_with_warnings"] += 1

                if result["errors"]:
                    summary["files_with_errors"] += 1

                summary["details"].append({"file": str(yaml_file), "result": result})

        return summary
