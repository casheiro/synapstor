"""
Matrix Embedding Framework (MEF) support for Synapstor.

This module provides parsing, validation, and processing capabilities
for MEF-formatted knowledge units (UKIs).
"""

from .parser import MEFParser
from .types import MEFDocument, MEFMetadata
from .validator import MEFValidator

__all__ = ["MEFParser", "MEFDocument", "MEFMetadata", "MEFValidator"]
