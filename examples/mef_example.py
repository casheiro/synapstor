#!/usr/bin/env python3
"""
Exemplo de uso do Matrix Embedding Framework (MEF) no Synapstor.

Este exemplo demonstra como:
- Ativar o suporte MEF
- Indexar arquivos UKI (Units of Knowledge Interlinked)
- Realizar buscas com metadados semânticos enriquecidos
- Navegar por relacionamentos entre UKIs
"""

import asyncio
import os
import tempfile
from pathlib import Path

from synapstor.qdrant import QdrantConnector, Entry
from synapstor.embeddings.factory import create_embedding_provider
from synapstor.settings import EmbeddingProviderSettings, QdrantSettings


def criar_exemplo_uki():
    """Cria um exemplo de arquivo UKI para demonstração."""
    conteudo_uki = """
id: unik-example-api-auth
title: Exemplo de Autenticação de API
domain: technical
type: pattern
context: implementation
content: |
  Este é um exemplo de como implementar autenticação JWT em APIs REST.
  
  ## Implementação Básica
  
  1. Configurar middleware de autenticação
  2. Criar endpoint de login
  3. Validar tokens em rotas protegidas
  
  ## Considerações de Segurança
  
  - Use algoritmos seguros (RS256, HS256)
  - Defina tempo de expiração apropriado
  - Implemente refresh tokens
  
examples:
  - input: "POST /auth/login com credentials válidas"
    output: "JWT token com expiração de 15 minutos"
  - input: "GET /protected com token válido"
    output: "Acesso autorizado aos dados"

intent_of_use:
  - validate_implementation
  - generate_authentication_code
  - security_review
  
use_case_stage:
  - design
  - implementation
  - testing
  - production

related_to:
  - unik-jwt-validation
  - unik-security-middleware
  - unik-api-error-handling

tags:
  - authentication
  - jwt
  - security
  - rest-api
"""

    # Criar diretório temporário para o exemplo
    temp_dir = Path(tempfile.mkdtemp(prefix="synapstor_mef_"))
    uki_file = temp_dir / "api-auth-example.yaml"

    with open(uki_file, "w", encoding="utf-8") as f:
        f.write(conteudo_uki.strip())

    return temp_dir, uki_file


async def demonstrar_mef():
    """Demonstra o uso do MEF no Synapstor."""
    print("🔍 Demonstração do Matrix Embedding Framework (MEF)")
    print("=" * 60)

    # Configurar MEF
    print("1. Configurando MEF...")

    # Configurar embeddings
    embedding_settings = EmbeddingProviderSettings()
    embedding_provider = create_embedding_provider(embedding_settings)

    # Configurar Qdrant (use URL local ou configure suas credenciais)
    qdrant_settings = QdrantSettings(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY"),
        collection_name="mef_example",
    )

    # Criar connector
    connector = QdrantConnector(
        qdrant_url=qdrant_settings.url,
        qdrant_api_key=qdrant_settings.api_key,
        collection_name=qdrant_settings.collection_name,
        embedding_provider=embedding_provider,
    )

    # Criar exemplo UKI
    print("2. Criando arquivo UKI de exemplo...")
    temp_dir, uki_file = criar_exemplo_uki()
    print(f"   📄 Arquivo UKI criado: {uki_file}")

    try:
        # Ler e processar o arquivo UKI
        print("3. Processando arquivo UKI...")
        with open(uki_file, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Quando MEF estiver implementado, aqui processaríamos os metadados YAML
        # Por enquanto, vamos simular os metadados enriquecidos
        metadados_mef = {
            "uki_id": "unik-example-api-auth",
            "uki_title": "Exemplo de Autenticação de API",
            "uki_domain": "technical",
            "uki_type": "pattern",
            "uki_context": "implementation",
            "intent_of_use": [
                "validate_implementation",
                "generate_authentication_code",
                "security_review",
            ],
            "use_case_stage": ["design", "implementation", "testing", "production"],
            "related_to": [
                "unik-jwt-validation",
                "unik-security-middleware",
                "unik-api-error-handling",
            ],
            "tags": ["authentication", "jwt", "security", "rest-api"],
            "arquivo": str(uki_file),
            "projeto": "mef_example",
            "tipo_conteudo": "uki_yaml",
        }

        # Armazenar no Qdrant
        print("4. Armazenando UKI no Qdrant...")
        entry = Entry(content=conteudo, metadata=metadados_mef)

        await connector.store(entry)
        print("   ✅ UKI armazenada com sucesso!")

        # Demonstrar busca semântica
        print("\n5. Realizando buscas semânticas...")

        queries = [
            "Como implementar autenticação JWT?",
            "Segurança em APIs REST",
            "Validação de tokens",
            "Middleware de autenticação",
        ]

        for query in queries:
            print(f"\n🔍 Consulta: '{query}'")
            resultados = await connector.search(query, limit=3)

            for i, resultado in enumerate(resultados, 1):
                score = getattr(resultado, "score", "N/A")
                metadata = getattr(resultado, "metadata", {})

                print(f"   {i}. Score: {score}")
                print(f"      UKI ID: {metadata.get('uki_id', 'N/A')}")
                print(f"      Título: {metadata.get('uki_title', 'N/A')}")
                print(f"      Domínio: {metadata.get('uki_domain', 'N/A')}")
                print(f"      Tipo: {metadata.get('uki_type', 'N/A')}")
                print(f"      Contexto: {metadata.get('uki_context', 'N/A')}")
                print(f"      Tags: {', '.join(metadata.get('tags', []))}")

        # Demonstrar busca por metadados específicos
        print("\n6. Demonstrando filtros MEF...")

        filtros_exemplos = [
            {"uki_domain": "technical"},
            {"uki_type": "pattern"},
            {"uki_context": "implementation"},
        ]

        for filtro in filtros_exemplos:
            print(f"\n🔍 Filtro MEF: {filtro}")
            # Aqui implementaríamos busca com filtros MEF
            print("   (Busca com filtros MEF seria implementada aqui)")

        print("\n🎉 Demonstração MEF concluída!")
        print("\n💡 Vantagens do MEF:")
        print("   • Metadados semânticos estruturados")
        print("   • Busca contextual aprimorada")
        print("   • Relacionamentos entre conhecimentos")
        print("   • Filtragem por domínio, tipo e contexto")
        print("   • Validação automática de estrutura")

    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")

    finally:
        # Limpar arquivos temporários
        try:
            uki_file.unlink()
            temp_dir.rmdir()
            print("\n🧹 Arquivos temporários removidos")
        except Exception as e:
            print(f"⚠️  Erro ao remover arquivos temporários: {e}")


def main():
    """Função principal para executar o exemplo."""
    print("Matrix Embedding Framework (MEF) - Exemplo de Uso")
    print("=" * 60)
    print()
    print("Este exemplo demonstra as capacidades do MEF no Synapstor:")
    print("• Estruturação de conhecimento em UKIs")
    print("• Metadados semânticos enriquecidos")
    print("• Busca contextual aprimorada")
    print("• Relacionamentos entre conhecimentos")
    print()

    # Verificar se o Qdrant está disponível
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    print(f"🔗 Conectando ao Qdrant em: {qdrant_url}")
    print("   (Certifique-se de que o Qdrant está rodando)")
    print()

    # Executar demonstração
    asyncio.run(demonstrar_mef())


if __name__ == "__main__":
    main()
