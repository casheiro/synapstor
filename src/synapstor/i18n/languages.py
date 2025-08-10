"""
Definições de idiomas suportados pelo Synapstor.
"""

from enum import Enum
from typing import Dict, Any


class Language(Enum):
    """Idiomas suportados pelo Synapstor."""

    PORTUGUESE = "pt"
    ENGLISH = "en"


class SupportedLanguages:
    """Informações sobre idiomas suportados."""

    LANGUAGE_INFO: Dict[Language, Dict[str, Any]] = {
        Language.PORTUGUESE: {
            "name": "Português",
            "code": "pt",
            "locale": "pt_BR",
            "rtl": False,
        },
        Language.ENGLISH: {
            "name": "English",
            "code": "en",
            "locale": "en_US",
            "rtl": False,
        },
    }

    @classmethod
    def get_language_by_code(cls, code: str) -> Language:
        """Gets language by code."""
        code = code.lower()
        for language in Language:
            if cls.LANGUAGE_INFO[language]["code"] == code:
                return language
        # Fallback to English if not found
        return Language.ENGLISH

    @classmethod
    def get_language_info(cls, language: Language) -> Dict[str, Any]:
        """Gets information about a language."""
        return cls.LANGUAGE_INFO[language]

    @classmethod
    def get_available_languages(cls) -> list[Language]:
        """Returns list of available languages."""
        return list(Language)
