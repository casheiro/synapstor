#!/usr/bin/env python3
"""
Exemplo de uso do sistema de internacionalização (i18n) do Synapstor

Este exemplo demonstra como usar o sistema de tradução em diferentes
cenários e idiomas.
"""

import asyncio
import os
import traceback
from src.synapstor.i18n import (
    get_translator,
    set_language,
    Language,
    SupportedLanguages,
    _,
)
from src.synapstor.settings import I18nSettings


def exemplo_basico():
    """Exemplo básico de uso do sistema de tradução."""
    print("🌍 Exemplo Básico de Internacionalização\n")

    # Obter tradutor
    translator = get_translator()

    # Tradução simples
    print("=== Português (padrão) ===")
    set_language(Language.PORTUGUESE)
    print(f"Título: {translator.translate('modo_synapstor.title')}")
    print(f"Sucesso: {translator.translate('common.success')}")
    print(f"Erro: {translator.translate('common.error')}")

    print("\n=== English ===")
    set_language(Language.ENGLISH)
    print(f"Title: {translator.translate('modo_synapstor.title')}")
    print(f"Success: {translator.translate('common.success')}")
    print(f"Error: {translator.translate('common.error')}")


def exemplo_interpolacao():
    """Exemplo de interpolação de variáveis."""
    print("\n🔧 Exemplo de Interpolação de Variáveis\n")

    translator = get_translator()

    # Português
    print("=== Português ===")
    set_language(Language.PORTUGUESE)

    tema = "Inteligência Artificial na Educação"
    print(f"Tema: {translator.translate('modo_synapstor.theme', theme=tema)}")

    info = "dados importantes sobre IA"
    print(f"Store: {translator.translate('tools.store.success', information=info)}")

    query = "machine learning"
    print(f"Find: {translator.translate('tools.find.no_results', query=query)}")

    # English
    print("\n=== English ===")
    set_language(Language.ENGLISH)
    print(f"Theme: {translator.translate('modo_synapstor.theme', theme=tema)}")
    print(f"Store: {translator.translate('tools.store.success', information=info)}")
    print(f"Find: {translator.translate('tools.find.no_results', query=query)}")


def exemplo_funcao_conveniencia():
    """Exemplo usando a função de conveniência _()."""
    print("\n⚡ Exemplo com Função de Conveniência _() \n")

    # Português
    set_language(Language.PORTUGUESE)
    print("=== Português ===")
    print(f"Carregando: {_('common.loading')}")
    print(f"Gerando: {_('common.generating')}")
    print(f"Concluído: {_('common.completed')}")

    # English
    set_language(Language.ENGLISH)
    print("\n=== English ===")
    print(f"Loading: {_('common.loading')}")
    print(f"Generating: {_('common.generating')}")
    print(f"Completed: {_('common.completed')}")


def exemplo_fallback():
    """Exemplo do sistema de fallback."""
    print("\n🔄 Exemplo de Sistema de Fallback\n")

    translator = get_translator()

    # Testar chave que não existe
    set_language(Language.PORTUGUESE)
    print("=== Testando chave inexistente ===")
    print(f"Chave inexistente: {translator.translate('chave.que.nao.existe')}")

    # Verificar se tradução existe
    print(f"\nChave existe? {translator.has_translation('common.success')}")
    print(f"Chave inexiste? {translator.has_translation('chave.que.nao.existe')}")


def exemplo_configuracao_ambiente():
    """Exemplo de configuração via variáveis de ambiente."""
    print("\n🌿 Exemplo de Configuração via Ambiente\n")

    # Simular diferentes configurações de ambiente
    ambientes = [
        ("pt", "Português"),
        ("en", "English"),
        ("es", "Español (fallback para inglês)"),
        ("fr", "Français (fallback para inglês)"),
    ]

    for lang_code, lang_name in ambientes:
        print(f"=== {lang_name} (SYNAPSTOR_LANGUAGE={lang_code}) ===")

        # Simular variável de ambiente
        os.environ["SYNAPSTOR_LANGUAGE"] = lang_code

        i18n_settings = I18nSettings()
        language = SupportedLanguages.get_language_by_code(i18n_settings.language)
        set_language(language)

        # Testar traduções
        translator = get_translator()
        print(f"  Título: {translator.translate('modo_synapstor.title')}")
        print(f"  Sucesso: {translator.translate('common.success')}")
        print()


def exemplo_modo_synapstor():
    """Exemplo específico do modo Synapstor."""
    print("\n🧠 Exemplo Específico do Modo Synapstor\n")

    translator = get_translator()
    tema = "Sustentabilidade em Startups de Tecnologia"

    for lang, lang_name in [
        (Language.PORTUGUESE, "Português"),
        (Language.ENGLISH, "English"),
    ]:
        print(f"=== {lang_name} ===")
        set_language(lang)

        print(f"Título: {translator.translate('modo_synapstor.title')}")
        print(f"Tema: {translator.translate('modo_synapstor.theme', theme=tema)}")
        print(f"Contexto: {translator.translate('modo_synapstor.context_header')}")
        print(
            f"Documentos: {translator.translate('modo_synapstor.total_documents', count=3)}"
        )
        print(f"Fase 1: {translator.translate('modo_synapstor.phase1_title')}")
        print(f"Fase 2: {translator.translate('modo_synapstor.phase2_title')}")
        print()


async def exemplo_plugin_async():
    """Exemplo de como usar i18n em plugins assíncronos."""
    print("\n🔌 Exemplo de Plugin Assíncrono\n")

    async def simular_plugin_function(tema: str, lang: Language):
        """Simula uma função de plugin que usa i18n."""
        set_language(lang)
        translator = get_translator()

        # Simular início do processamento
        print(
            f"[{lang.value.upper()}] {translator.translate('modo_synapstor.debug.starting', theme=tema)}"
        )

        # Simular delay de processamento
        await asyncio.sleep(0.1)

        # Simular consulta RAG
        print(
            f"[{lang.value.upper()}] {translator.translate('modo_synapstor.debug.consulting_rag')}"
        )
        await asyncio.sleep(0.1)

        # Simular construção de prompt
        print(
            f"[{lang.value.upper()}] {translator.translate('modo_synapstor.debug.building_prompt', count=4)}"
        )
        await asyncio.sleep(0.1)

        # Simular sucesso
        print(
            f"[{lang.value.upper()}] {translator.translate('modo_synapstor.debug.success')}"
        )

        return translator.translate("common.completed")

    # Executar em português e inglês
    tema = "Tecnologia Sustentável"

    resultado_pt = await simular_plugin_function(tema, Language.PORTUGUESE)
    resultado_en = await simular_plugin_function(tema, Language.ENGLISH)

    print(f"\nResultado PT: {resultado_pt}")
    print(f"Resultado EN: {resultado_en}")


def exemplo_validacao():
    """Exemplo de validação de traduções."""
    print("\n✅ Exemplo de Validação de Traduções\n")

    translator = get_translator()

    # Lista de chaves importantes para testar
    chaves_importantes = [
        "common.success",
        "common.error",
        "tools.store.description",
        "tools.find.description",
        "modo_synapstor.title",
        "modo_synapstor.description",
        "server.starting",
        "server.started",
    ]

    # Testar em ambos os idiomas
    for lang, lang_name in [
        (Language.PORTUGUESE, "Português"),
        (Language.ENGLISH, "English"),
    ]:
        print(f"=== Validação {lang_name} ===")
        set_language(lang)

        missing_keys = []
        valid_keys = []

        for key in chaves_importantes:
            if translator.has_translation(key):
                valid_keys.append(key)
                # Mostrar primeira tradução encontrada como exemplo
                if len(valid_keys) == 1:
                    translation = translator.translate(key)
                    print(f"  Exemplo: '{key}' -> '{translation}'")
            else:
                missing_keys.append(key)

        print(f"  ✅ Chaves válidas: {len(valid_keys)}")
        if missing_keys:
            print(f"  ❌ Chaves ausentes: {missing_keys}")
        else:
            print("  🎉 Todas as chaves testadas estão presentes!")
        print()


def exemplo_performance():
    """Exemplo de teste de performance."""
    print("\n⚡ Exemplo de Performance\n")

    import time

    translator = get_translator()

    # Teste de tradução simples
    start_time = time.time()
    for i in range(1000):
        translator.translate("common.success")
    simple_time = time.time() - start_time

    # Teste de tradução com interpolação
    start_time = time.time()
    for i in range(1000):
        translator.translate("modo_synapstor.theme", theme="Teste")
    interpolation_time = time.time() - start_time

    print(f"Traduções simples (1000x): {simple_time:.4f}s")
    print(f"Traduções com interpolação (1000x): {interpolation_time:.4f}s")
    print(f"Média tradução simples: {simple_time/1000*1000:.4f}ms")
    print(f"Média tradução interpolação: {interpolation_time/1000*1000:.4f}ms")


async def main():
    """Função principal que executa todos os exemplos."""
    print("🌍 Exemplos do Sistema de Internacionalização do Synapstor")
    print("=" * 60)

    try:
        exemplo_basico()
        exemplo_interpolacao()
        exemplo_funcao_conveniencia()
        exemplo_fallback()
        exemplo_configuracao_ambiente()
        exemplo_modo_synapstor()
        await exemplo_plugin_async()
        exemplo_validacao()
        exemplo_performance()

        print("\n✅ Todos os exemplos executados com sucesso!")
        print("\n💡 Para usar em seu código:")
        print("   from synapstor.i18n import get_translator, set_language")
        print("   translator = get_translator()")
        print("   message = translator.translate('sua.chave', variavel='valor')")

    except (ValueError, KeyError, RuntimeError) as e:
        print(f"\n❌ Erro durante execução dos exemplos: {e}")

        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Executando exemplos de internacionalização...")
    asyncio.run(main())
