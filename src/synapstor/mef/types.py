"""
Type definitions for Matrix Embedding Framework (MEF).
"""

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class MEFExample(BaseModel):
    """Example structure within a MEF document."""

    input: str
    output: str


class MEFDocument(BaseModel):
    """
    Represents a MEF UKI (Unit of Knowledge Interlinked).

    This model validates the structure of MEF YAML documents according
    to the Matrix Embedding Framework specification.
    """

    id: str = Field(..., description="Unique identifier in format unik-[domain]-[slug]")
    title: str = Field(..., description="Descriptive title of the UKI")
    domain: str = Field(
        ...,
        description="Knowledge domain (product, business, technical, strategy, culture)",
    )
    type: str = Field(
        ...,
        description="Content type (business_rule, function, template, guideline, pattern, decision, example)",
    )
    context: str = Field(
        ...,
        description="Usage context (discovery, implementation, refinement, qa, documentation, support)",
    )
    intent_of_use: List[str] = Field(
        default_factory=list, description="List of intended use cases"
    )
    use_case_stage: List[str] = Field(
        default_factory=list, description="List of applicable stages"
    )
    language: str = Field(
        default="en_US", description="Content language (e.g., pt_BR, en_US)"
    )
    content: str = Field(..., description="Main content of the UKI")
    examples: List[MEFExample] = Field(
        default_factory=list, description="Usage examples"
    )
    related_to: List[str] = Field(
        default_factory=list, description="IDs of related UKIs"
    )
    last_validation: Optional[date] = Field(
        default=None, description="Last validation date"
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v):
        """Validate ID follows MEF format."""
        if not v.startswith("unik-"):
            raise ValueError('ID must start with "unik-"')
        parts = v.split("-")
        if len(parts) < 3:
            raise ValueError('ID must follow format "unik-[domain]-[slug]"')
        return v

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v):
        """Validate domain is supported."""
        valid_domains = ["product", "business", "technical", "strategy", "culture"]
        if v not in valid_domains:
            raise ValueError(f"Domain must be one of: {valid_domains}")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Validate type is supported."""
        valid_types = [
            "business_rule",
            "function",
            "template",
            "guideline",
            "pattern",
            "decision",
            "example",
        ]
        if v not in valid_types:
            raise ValueError(f"Type must be one of: {valid_types}")
        return v

    @field_validator("context")
    @classmethod
    def validate_context(cls, v):
        """Validate context is supported."""
        valid_contexts = [
            "discovery",
            "implementation",
            "refinement",
            "qa",
            "documentation",
            "support",
        ]
        if v not in valid_contexts:
            raise ValueError(f"Context must be one of: {valid_contexts}")
        return v


class MEFMetadata(BaseModel):
    """
    Enhanced metadata structure for MEF documents.

    Extends standard file metadata with MEF-specific fields.
    """

    # Standard metadata (from existing indexer)
    projeto: str
    caminho_absoluto: str
    caminho_relativo: str
    nome_arquivo: str
    extensao: str
    tamanho_bytes: int
    data_modificacao: Optional[str] = None

    # MEF-specific metadata
    is_mef_document: bool = False
    mef_id: Optional[str] = None
    mef_domain: Optional[str] = None
    mef_type: Optional[str] = None
    mef_context: Optional[str] = None
    mef_language: Optional[str] = None
    mef_intent_of_use: List[str] = Field(default_factory=list)
    mef_use_case_stage: List[str] = Field(default_factory=list)
    mef_related_to: List[str] = Field(default_factory=list)
    mef_last_validation: Optional[str] = None
    mef_examples_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Qdrant storage."""
        return self.dict(exclude_unset=True, exclude_none=True)
