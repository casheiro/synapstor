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
        """Carrega arquivos de tradução."""
        translations_dir = Path(__file__).parent / "translations"
        
        for lang in Language:
            lang_info = SupportedLanguages.get_language_info(lang)
            lang_file = translations_dir / f"{lang_info['code']}.json"
            
            try:
                if lang_file.exists():
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self._translations[lang] = json.load(f)
                else:
                    logger.warning(f"Translation file not found: {lang_file}")
                    self._translations[lang] = {}
            except Exception as e:
                logger.error(f"Error loading translation file {lang_file}: {e}")
                self._translations[lang] = {}
    
    def set_language(self, language: Language):
        """Define o idioma atual."""
        with self._lock:
            self._language = language
    
    def get_language(self) -> Language:
        """Retorna o idioma atual."""
        return self._language
    
    def translate(self, key: str, **kwargs) -> str:
        """
        Traduz uma chave para o idioma atual.
        
        Args:
            key: Chave de tradução (ex: "tools.store.success")
            **kwargs: Variáveis para interpolação na string
            
        Returns:
            String traduzida ou a chave original se não encontrada
        """
        with self._lock:
            translations = self._translations.get(self._language, {})
            
            # Navegar pela estrutura aninhada usando pontos
            keys = key.split('.')
            value = translations
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    # Se não encontrar, tentar inglês como fallback
                    if self._language != Language.ENGLISH:
                        return self._get_fallback_translation(key, **kwargs)
                    return key  # Retorna a chave se não encontrar tradução
            
            # Interpolar variáveis se necessário
            if isinstance(value, str) and kwargs:
                try:
                    return value.format(**kwargs)
                except KeyError as e:
                    logger.warning(f"Missing variable {e} for translation key: {key}")
                    return value
            
            return str(value)
    
    def _get_fallback_translation(self, key: str, **kwargs) -> str:
        """Obtém tradução em inglês como fallback."""
        en_translations = self._translations.get(Language.ENGLISH, {})
        
        keys = key.split('.')
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
        """Verifica se existe tradução para uma chave."""
        translations = self._translations.get(self._language, {})
        keys = key.split('.')
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
    """Retorna a instância global do tradutor."""
    global _global_translator
    
    with _translator_lock:
        if _global_translator is None:
            _global_translator = Translator()
        return _global_translator


def set_language(language: Language):
    """Define o idioma global."""
    translator = get_translator()
    translator.set_language(language)


def _(key: str, **kwargs) -> str:
    """
    Função de conveniência para tradução.
    
    Args:
        key: Chave de tradução
        **kwargs: Variáveis para interpolação
        
    Returns:
        String traduzida
    """
    return get_translator().translate(key, **kwargs)