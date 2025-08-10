"""
Sistema de tradução para o Synapstor.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock

from .languages import Language, SupportedLanguages

logger = logging.getLogger(__name__)


class Translator:
    """
    Classe principal para gerenciar traduções no Synapstor.
    """

    def __init__(self, language: Language = Language.ENGLISH):
        self._language = language
        self._translations: Dict[Language, Dict[str, Any]] = {}
        self._lock = Lock()
        self._load_translations()

    def _load_translations(self):
        """Loads translation files."""
        translations_dir = Path(__file__).parent / "translations"

        for lang in Language:
            lang_info = SupportedLanguages.get_language_info(lang)
            lang_file = translations_dir / f"{lang_info['code']}.json"

            try:
                if lang_file.exists():
                    with open(lang_file, "r", encoding="utf-8") as f:
                        self._translations[lang] = json.load(f)
                else:
                    logger.warning("Translation file not found: %s", lang_file)
                    self._translations[lang] = {}
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Error loading translation file %s: %s", lang_file, e)
                self._translations[lang] = {}

    def set_language(self, language: Language):
        """Sets the current language."""
        with self._lock:
            self._language = language

    def get_language(self) -> Language:
        """Returns the current language."""
        return self._language

    def translate(self, key: str, **kwargs) -> str:
        """
        Translates a key to the current language.

        Args:
            key: Translation key (e.g.: "tools.store.success")
            **kwargs: Variables for string interpolation

        Returns:
            Translated string or original key if not found
        """
        with self._lock:
            translations = self._translations.get(self._language, {})

            # Navigate nested structure using dots
            keys = key.split(".")
            value = translations

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    # If not found, try English as fallback
                    if self._language != Language.ENGLISH:
                        return self._get_fallback_translation(key, **kwargs)
                    return key  # Return key if translation not found

            # Interpolate variables if necessary
            if isinstance(value, str) and kwargs:
                try:
                    return value.format(**kwargs)
                except KeyError as e:
                    logger.warning(
                        "Missing variable %s for translation key: %s", e, key
                    )
                    return value

            return str(value)

    def _get_fallback_translation(self, key: str, **kwargs) -> str:
        """Gets English translation as fallback."""
        en_translations = self._translations.get(Language.ENGLISH, {})

        keys = key.split(".")
        value = en_translations

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key

        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except KeyError:
                return str(value)

        return str(value)

    def has_translation(self, key: str) -> bool:
        """Checks if translation exists for a key."""
        translations = self._translations.get(self._language, {})
        keys = key.split(".")
        value = translations

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return False

        return True


# Instância global do tradutor
_global_translator: Optional[Translator] = None
_translator_lock = Lock()


def get_translator() -> Translator:
    """Returns the global translator instance."""
    global _global_translator

    with _translator_lock:
        if _global_translator is None:
            _global_translator = Translator()
        return _global_translator


def set_language(language: Language):
    """Sets the global language."""
    translator = get_translator()
    translator.set_language(language)


def _(key: str, **kwargs) -> str:
    """
    Convenience function for translation.

    Args:
        key: Translation key
        **kwargs: Variables for interpolation

    Returns:
        Translated string
    """
    return get_translator().translate(key, **kwargs)
