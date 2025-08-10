"""
Sistema de Internacionalização (i18n) para Synapstor

Este módulo fornece funcionalidades de internacionalização para o Synapstor,
permitindo suporte a múltiplos idiomas para interfaces e mensagens do sistema.
"""

from .translator import Translator, get_translator, set_language, _
from .languages import Language, SupportedLanguages

__all__ = [
    "Translator",
    "get_translator",
    "set_language",
    "Language",
    "SupportedLanguages",
    "_",
]
