#!/usr/bin/env python3
"""
Exemplo de uso do Modo Synapstor

Este arquivo demonstra como usar o modo_synapstor para criar
debates multidisciplinares com recuperação automática de contexto.
"""

import asyncio
import json
from synapstor.qdrant import QdrantConnector, Entry
from synapstor.embeddings.factory import create_embedding_provider
from synapstor.settings import EmbeddingProviderSettings, QdrantSettings

async def exemplo_modo_synapstor():
    """
    Exemplo de uso completo do modo Synapstor.
    """
    print("🚀 Exemplo: Modo Synapstor - Raciocínio Multidisciplinar com RAG\n")
    
    # 1. Configurar ambiente de teste
    print("📚 1. Configurando ambiente de teste...")
    
    # Configurações (ajuste conforme seu ambiente)
    qdrant_settings = QdrantSettings()
    embedding_settings = EmbeddingProviderSettings()
    
    # Criar provedor de embeddings e conector
    embedding_provider = create_embedding_provider(embedding_settings)
    qdrant_connector = QdrantConnector(
        qdrant_url="http://localhost:6333",
        collection_name="exemplo_synapstor",
        embedding_provider=embedding_provider
    )
    
    # 2. Adicionar contexto de exemplo
    print("📄 2. Adicionando contexto de exemplo ao Qdrant...")
    
    documentos_exemplo = [
        Entry(
            content="A inteligência artificial na educação pode personalizar o aprendizado, adaptando-se ao ritmo e estilo de cada estudante. Ferramentas como sistemas tutores inteligentes e plataformas adaptativas permitem identificar lacunas de conhecimento e sugerir conteúdos específicos.",
            metadata={
                "projeto": "educacao_ai",
                "nome_arquivo": "ia_personalizacao.md",
                "categoria": "educacao",
                "autor": "Dr. Silva"
            }
        ),
        Entry(
            content="Os desafios éticos da IA na educação incluem privacidade de dados dos estudantes, viés algorítmico na avaliação, e a necessidade de manter o elemento humano no processo educativo. É crucial desenvolver frameworks éticos robustos.",
            metadata={
                "projeto": "educacao_ai",
                "nome_arquivo": "etica_ai_educacao.md",
                "categoria": "etica",
                "autor": "Prof. Santos"
            }
        ),
        Entry(
            content="Implementações práticas de IA em sala de aula mostram resultados promissores. Chatbots educacionais, sistemas de correção automática e análise de sentimento em fóruns estudantis são exemplos de aplicações bem-sucedidas.",
            metadata={
                "projeto": "educacao_ai",
                "nome_arquivo": "casos_praticos.md",
                "categoria": "implementacao",
                "autor": "Equipe Tech"
            }
        )
    ]
    
    # Armazenar documentos
    for doc in documentos_exemplo:
        await qdrant_connector.store(doc, collection_name="exemplo_synapstor")
    
    print(f"✅ {len(documentos_exemplo)} documentos adicionados com sucesso!")
    
    # 3. Simular uso do modo Synapstor
    print("\n🧠 3. Simulando uso do modo Synapstor...")
    
    # Tema para análise
    tema = "Inteligência Artificial na Educação: Oportunidades e Desafios"
    
    # Importar as classes do plugin
    from synapstor.plugins.tool_modo_synapstor import (
        GeradorPersonalidades, 
        ConsultorRAG, 
        ConstrutorPrompt,
        ConfiguracaoDebate
    )
    
    # Configuração
    configuracao = ConfiguracaoDebate(
        max_personalidades=4,
        limite_documentos_rag=3,
        namespace_padrao="exemplo_synapstor"
    )
    
    # Detectar domínio e gerar personalidades
    dominio = GeradorPersonalidades.detectar_dominio(tema)
    personalidades = GeradorPersonalidades.gerar_personalidades(tema, configuracao)
    
    print(f"🎯 Domínio detectado: {dominio}")
    print(f"👥 Personalidades geradas: {len(personalidades)}")
    for p in personalidades:
        print(f"   • {p.nome} - {p.expertise}")
    
    # Consultar contexto RAG
    consultor_rag = ConsultorRAG(qdrant_connector)
    contexto_rag = await consultor_rag.consultar_contexto(tema, configuracao)
    
    print(f"\n📚 Contexto RAG recuperado: {contexto_rag.total_encontrados} documentos")
    
    # Construir prompt final
    prompt_final = ConstrutorPrompt.construir_prompt(
        tema=tema,
        personalidades=personalidades,
        contexto_rag=contexto_rag,
        dominio=dominio
    )
    
    # 4. Exibir resultado
    print("\n" + "="*80)
    print("🎭 PROMPT GERADO PELO MODO SYNAPSTOR")
    print("="*80)
    print(prompt_final)
    print("="*80)
    
    # 5. Estatísticas
    print(f"\n📊 Estatísticas:")
    print(f"   • Comprimento do prompt: {len(prompt_final)} caracteres")
    print(f"   • Personalidades ativas: {len(personalidades)}")
    print(f"   • Documentos RAG utilizados: {contexto_rag.total_encontrados}")
    print(f"   • Domínio especializado: {dominio.title()}")
    
    print("\n✅ Exemplo concluído com sucesso!")
    print("\n💡 Para usar em produção:")
    print("   1. Configure o Qdrant com seus dados reais")
    print("   2. Use via MCP: synapstor-server")
    print("   3. Chame a ferramenta: modo-synapstor")


async def exemplo_personalidades_customizadas():
    """
    Exemplo de como criar personalidades customizadas.
    """
    print("\n🎨 Exemplo: Personalidades Customizadas\n")
    
    from synapstor.plugins.tool_modo_synapstor import Personalidade
    
    # Criar personalidades customizadas para um projeto específico
    personalidades_custom = [
        Personalidade(
            nome="Arquiteto de Software Sênior",
            expertise="Arquitetura de Sistemas Distribuídos",
            papel="Projetista de Soluções Escaláveis",
            estilo="técnico-pragmático",
            perspectiva="performance e maintibilidade"
        ),
        Personalidade(
            nome="UX Designer Principal", 
            expertise="Experiência do Usuário e Design Thinking",
            papel="Defensor da Usabilidade",
            estilo="empático-visual",
            perspectiva="centrada no usuário"
        ),
        Personalidade(
            nome="DevOps Engineer",
            expertise="Infraestrutura e Automação",
            papel="Facilitador da Entrega Contínua",
            estilo="operacional-resiliente", 
            perspectiva="confiabilidade e automação"
        )
    ]
    
    print("👥 Personalidades Customizadas Criadas:")
    for i, p in enumerate(personalidades_custom, 1):
        print(f"{i}. {p.nome}")
        print(f"   Expertise: {p.expertise}")
        print(f"   Papel: {p.papel}")
        print(f"   Estilo: {p.estilo}")
        print(f"   Perspectiva: {p.perspectiva}\n")
    
    # Converter para JSON (útil para configurações)
    json_config = json.dumps([
        {
            "nome": p.nome,
            "expertise": p.expertise,
            "papel": p.papel,
            "estilo": p.estilo,
            "perspectiva": p.perspectiva
        } for p in personalidades_custom
    ], indent=2, ensure_ascii=False)
    
    print("📋 Configuração JSON para personalidades customizadas:")
    print(json_config)


async def main():
    """
    Função principal que executa todos os exemplos.
    """
    try:
        await exemplo_modo_synapstor()
        await exemplo_personalidades_customizadas()
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        print("\n💡 Dicas para resolução:")
        print("   1. Verifique se o Qdrant está rodando em localhost:6333")
        print("   2. Instale as dependências: pip install -e '.[all]'")
        print("   3. Configure as variáveis de ambiente apropriadas")


if __name__ == "__main__":
    print("🎭 Exemplos do Modo Synapstor")
    print("=" * 50)
    
    # Executar exemplos
    asyncio.run(main())