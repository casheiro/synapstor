"""
Plugin Modo Synapstor - Sistema de Raciocínio Multidisciplinar com RAG

Este plugin implementa o modo_synapstor, que ativa um sistema de raciocínio
multidisciplinar baseado em múltiplas personalidades especializadas que
debatem colaborativamente, utilizando recuperação automática de contexto
via RAG do banco Qdrant.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from mcp.server.fastmcp import Context

from synapstor.i18n import get_translator

logger = logging.getLogger(__name__)

#############################################################################
# SECTION 1: ESTRUTURAS DE DADOS                                            #
#############################################################################

# NOTA: Personalidade como dataclass foi removida.
# Personalidades customizadas são fornecidas diretamente como JSON.
# Exemplo de JSON para personalidades customizadas:
# [
#   {
#     "nome": "Nome do Especialista",
#     "expertise": "Área de conhecimento",
#     "papel": "Função no debate",
#     "estilo": "Tom de comunicação",
#     "perspectiva": "Ângulo de análise"
#   }
# ]


@dataclass
class ContextoRAG:
    """
    Representa o contexto recuperado via RAG do Qdrant.
    """
    documentos: List[Dict[str, Any]]
    query_original: str
    total_encontrados: int
    relevancia_minima: float = 0.0


@dataclass
class ConfiguracaoDebate:
    """
    Configurações para o modo de debate multidisciplinar.
    """
    max_personalidades: int = 5
    min_personalidades: int = 3
    limite_documentos_rag: int = 5
    namespace_padrao: str = "projetos_ativos"
    relevancia_minima: float = 0.3


#############################################################################
# SECTION 2: GERADOR DE PERSONALIDADES DINÂMICO                             #
#############################################################################

class GeradorPersonalidades:
    """
    Gera personalidades especializadas dinamicamente através de instruções para o LLM.
    """
    
    @classmethod
    def _get_personality_generator_prompt(cls) -> str:
        """Obtém o prompt do gerador de personalidades traduzido."""
        translator = get_translator()
        return translator.translate("modo_synapstor.personality_generator.instruction")

    @classmethod
    def gerar_prompt_personalidades(cls, tema: str, num_personalidades: int) -> str:
        """
        Gera o prompt para o LLM criar personalidades dinamicamente.
        """
        prompt_template = cls._get_personality_generator_prompt()
        return prompt_template.format(
            theme=tema,
            num_personalities=num_personalidades
        )


#############################################################################
# SECTION 3: CONSULTA RAG AO QDRANT                                         #
#############################################################################

class ConsultorRAG:
    """
    Responsável pela consulta RAG ao banco Qdrant.
    """
    
    def __init__(self, qdrant_connector):
        """
        Inicializa o consultor RAG com o conector Qdrant.
        """
        self.qdrant_connector = qdrant_connector
    
    async def consultar_contexto(
        self, 
        tema: str, 
        configuracao: ConfiguracaoDebate,
        filtros: Optional[Dict[str, Any]] = None
    ) -> ContextoRAG:
        """
        Consulta o Qdrant para recuperar contexto relevante sobre o tema.
        """
        try:
            # Preparar query melhorada baseada no tema
            query_expandida = self._expandir_query(tema)
            
            # Realizar busca no Qdrant
            resultados = await self.qdrant_connector.search(
                query=query_expandida,
                limit=configuracao.limite_documentos_rag,
                collection_name=configuracao.namespace_padrao
            )
            
            # Processar resultados
            documentos_processados = []
            for entrada in resultados:
                doc_processado = {
                    "conteudo": entrada.content,
                    "metadata": entrada.metadata or {},
                    "relevancia": 1.0  # Qdrant não retorna score por padrão no FastMCP
                }
                documentos_processados.append(doc_processado)
            
            return ContextoRAG(
                documentos=documentos_processados,
                query_original=tema,
                total_encontrados=len(documentos_processados),
                relevancia_minima=configuracao.relevancia_minima
            )
            
        except Exception as e:
            logger.error(f"Erro na consulta RAG: {e}")
            # Retornar contexto vazio em caso de erro
            return ContextoRAG(
                documentos=[],
                query_original=tema,
                total_encontrados=0,
                relevancia_minima=configuracao.relevancia_minima
            )
    
    def _expandir_query(self, tema: str) -> str:
        """
        Expande a query do tema com termos relacionados para melhor recuperação.
        """
        # Adicionar contexto semântico básico
        expansoes = [
            f"conceitos sobre {tema}",
            f"aspectos de {tema}",
            f"características de {tema}",
            f"princípios de {tema}",
            tema  # Query original
        ]
        
        # Retornar a query original com contexto adicional
        return f"{tema} - {' '.join(expansoes[:2])}"


#############################################################################
# SECTION 4: CONSTRUTOR DE PROMPT                                           #
#############################################################################

class ConstrutorPrompt:
    """
    Constrói o prompt final do modo Synapstor com geração dinâmica de personalidades.
    """
    
    @classmethod
    def _build_dynamic_template(cls, tema: str) -> str:
        """Constrói o template dinâmico traduzido."""
        translator = get_translator()
        
        template = f"""{translator.translate("modo_synapstor.title")}

🧠 {translator.translate("modo_synapstor.theme", theme=tema)}

📚 {translator.translate("modo_synapstor.context_header")}
{{contexto_qdrant}}

🎭 {translator.translate("modo_synapstor.phase1_title")}
{{prompt_personalidades}}

🎯 {translator.translate("modo_synapstor.phase2_title")}

{translator.translate("modo_synapstor.phase2_presentation")}

{translator.translate("modo_synapstor.phase2_analysis", theme=tema)}
"""
        
        # Adicionar bullets da análise
        for bullet in translator.translate("modo_synapstor.phase2_analysis_bullets"):
            template += f"   - {bullet}\n"
        
        template += f"""
{translator.translate("modo_synapstor.phase2_debate")}
"""
        
        # Adicionar bullets do debate
        for bullet in translator.translate("modo_synapstor.phase2_debate_bullets"):
            template += f"   - {bullet}\n"
        
        template += f"""
{translator.translate("modo_synapstor.phase2_synthesis")}
"""
        
        # Adicionar bullets da síntese
        for bullet in translator.translate("modo_synapstor.phase2_synthesis_bullets"):
            template += f"   - {bullet}\n"
        
        template += f"""
📝 {translator.translate("modo_synapstor.metadata_title")}
- {translator.translate("modo_synapstor.metadata_generated", timestamp="{{timestamp}}")}
- {translator.translate("modo_synapstor.metadata_documents", count="{{num_documentos}}")}
- {translator.translate("modo_synapstor.metadata_personalities", count="{{num_personalidades}}")}

🚀 {translator.translate("modo_synapstor.execute_instruction", theme=tema)}"""
        
        return template

    @classmethod
    def construir_prompt_dinamico(
        cls,
        tema: str,
        num_personalidades: int,
        contexto_rag: ContextoRAG
    ) -> str:
        """
        Constrói o prompt final do modo Synapstor com geração dinâmica de personalidades.
        """
        # Formatar contexto Qdrant
        contexto_formatado = cls._formatar_contexto_qdrant(contexto_rag)
        
        # Gerar prompt para criação de personalidades
        prompt_personalidades = GeradorPersonalidades.gerar_prompt_personalidades(
            tema=tema,
            num_personalidades=num_personalidades
        )
        
        # Construir template dinâmico traduzido
        template = cls._build_dynamic_template(tema)
        
        # Construir prompt final
        return template.format(
            contexto_qdrant=contexto_formatado,
            prompt_personalidades=prompt_personalidades,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            num_documentos=contexto_rag.total_encontrados,
            num_personalidades=num_personalidades
        )
    
    @classmethod
    def _formatar_contexto_qdrant(cls, contexto: ContextoRAG) -> str:
        """
        Formata o contexto recuperado do Qdrant.
        """
        translator = get_translator()
        
        if not contexto.documentos:
            return translator.translate("modo_synapstor.no_context")
        
        contexto_str = f"📊 {translator.translate('modo_synapstor.total_documents', count=contexto.total_encontrados)}\n\n"
        
        for i, doc in enumerate(contexto.documentos, 1):
            metadata = doc.get("metadata", {})
            projeto = metadata.get("projeto", "")
            arquivo = metadata.get("nome_arquivo", "")
            
            fonte = f" {translator.translate('modo_synapstor.source_prefix', source=f'{projeto}/{arquivo}')}" if projeto or arquivo else ""
            contexto_str += f"📄 {translator.translate('modo_synapstor.document_prefix', number=i)}{fonte}:\n{doc['conteudo'][:500]}{'...' if len(doc['conteudo']) > 500 else ''}\n\n"
        
        return contexto_str.strip()
    


#############################################################################
# SECTION 5: FERRAMENTA PRINCIPAL                                           #
#############################################################################

async def modo_synapstor(
    ctx: Context,
    tema: str,
    max_personalidades: int = 4,
    limite_documentos: int = 5,
    namespace: str = "",
    incluir_contexto_debug: bool = False
) -> str:
    """
    Ativa o modo Synapstor - sistema de raciocínio multidisciplinar com RAG.
    
    Esta ferramenta MCP constrói um prompt estruturado que instrui o LLM cliente a:
    1) Gerar personalidades especializadas dinamicamente baseadas no tema
    2) Executar um debate multidisciplinar usando contexto RAG recuperado do Qdrant
    3) Produzir análise multifacetada com perspectivas complementares
    
    O Synapstor fornece o contexto RAG e as instruções; o LLM executa o raciocínio.
    
    :param ctx: Contexto da requisição MCP
    :param tema: Tema principal para análise multidisciplinar
    :param max_personalidades: Número de especialistas a serem gerados (padrão: 4)
    :param limite_documentos: Limite de documentos RAG a recuperar (padrão: 5)
    :param namespace: Namespace/coleção Qdrant para busca (padrão: usa config do servidor)
    :param incluir_contexto_debug: Se deve incluir informações técnicas de debug
    :return: Prompt estruturado que instrui o LLM a executar o modo Synapstor
    """
    translator = get_translator()
    await ctx.debug(translator.translate("modo_synapstor.debug.starting", theme=tema))
    
    try:
        # Usar namespace padrão do servidor se não especificado
        namespace_final = namespace or _server_instance.qdrant_settings.collection_name or "synapstor"
        
        # Configuração do debate
        configuracao = ConfiguracaoDebate(
            max_personalidades=max_personalidades,
            limite_documentos_rag=limite_documentos,
            namespace_padrao=namespace_final
        )
        
        # Acessar o conector Qdrant através da referência global do servidor
        # Esta referência será definida na função setup_tools
        qdrant_connector = _server_instance.qdrant_connector
        
        # Inicializar consultor RAG
        consultor_rag = ConsultorRAG(qdrant_connector)
        
        # Recuperar contexto via RAG
        await ctx.debug(translator.translate("modo_synapstor.debug.consulting_rag"))
        contexto_rag = await consultor_rag.consultar_contexto(tema, configuracao)
        
        # Construir prompt final com geração dinâmica de personalidades
        await ctx.debug(translator.translate("modo_synapstor.debug.building_prompt", count=max_personalidades))
        
        prompt_final = ConstrutorPrompt.construir_prompt_dinamico(
            tema=tema,
            num_personalidades=max_personalidades,
            contexto_rag=contexto_rag
        )
        
        # Adicionar contexto de debug se solicitado
        if incluir_contexto_debug:
            debug_info = f"\n\n🔧 Debug Info:\n"
            debug_info += f"- Configuração: {asdict(configuracao)}\n"
            debug_info += f"- Personalidades solicitadas: {max_personalidades}\n"
            debug_info += f"- Documentos RAG encontrados: {contexto_rag.total_encontrados}\n"
            debug_info += f"- Namespace utilizado: {namespace_final}\n"
            prompt_final += debug_info
        
        await ctx.debug(translator.translate("modo_synapstor.debug.success"))
        return prompt_final
        
    except Exception as e:
        error_msg = f"Erro no modo Synapstor: {str(e)}"
        await ctx.debug(error_msg)
        logger.error(error_msg)
        
        # Retornar prompt de fallback traduzido
        fallback_prompt = f"""{translator.translate("modo_synapstor.errors.initialization")}

{translator.translate("modo_synapstor.errors.error_occurred", error=str(e))}

{translator.translate("modo_synapstor.errors.fallback_activated")}

🧠 {translator.translate("modo_synapstor.theme", theme=tema)}

{translator.translate("modo_synapstor.errors.fallback_personalities")}
- {translator.translate("modo_synapstor.errors.technical_expert")}
- {translator.translate("modo_synapstor.errors.strategic_thinker")}
- {translator.translate("modo_synapstor.errors.analytical_critic")}

{translator.translate("modo_synapstor.errors.fallback_instructions", theme=tema)}
"""
        return fallback_prompt


#############################################################################
# SECTION 6: FERRAMENTAS AUXILIARES                                         #
#############################################################################

async def info_modo_synapstor(ctx: Context) -> List[str]:
    """
    Fornece informações sobre como o modo Synapstor funciona.
    
    :param ctx: Contexto da requisição MCP
    :return: Informações sobre o funcionamento do modo Synapstor
    """
    await ctx.debug("Fornecendo informações sobre o modo Synapstor")
    
    translator = get_translator()
    
    info_lines = [
        translator.translate("modo_synapstor.info.title"),
        "",
        translator.translate("modo_synapstor.info.dynamic_generation"),
    ]
    
    for bullet in translator.translate("modo_synapstor.info.dynamic_bullets"):
        info_lines.append(f"   {bullet}")
    
    info_lines.extend([
        "",
        translator.translate("modo_synapstor.info.rag_retrieval"),
    ])
    
    for bullet in translator.translate("modo_synapstor.info.rag_bullets"):
        info_lines.append(f"   {bullet}")
    
    info_lines.extend([
        "",
        translator.translate("modo_synapstor.info.debate"),
    ])
    
    for bullet in translator.translate("modo_synapstor.info.debate_bullets"):
        info_lines.append(f"   {bullet}")
    
    info_lines.extend([
        "",
        translator.translate("modo_synapstor.info.advantages_title"),
    ])
    
    for advantage in translator.translate("modo_synapstor.info.advantages"):
        info_lines.append(f"   {advantage}")
    
    info_lines.extend([
        "",
        translator.translate("modo_synapstor.info.examples_title"),
    ])
    
    for example in translator.translate("modo_synapstor.info.examples"):
        info_lines.append(f"   {example}")
    
    return info_lines


async def configurar_synapstor(
    ctx: Context,
    tema: str,
    personalidades_customizadas: Optional[str] = None
) -> str:
    """
    Permite configuração customizada do modo Synapstor.
    
    :param ctx: Contexto da requisição MCP
    :param tema: Tema para análise
    :param personalidades_customizadas: JSON com personalidades customizadas
    :return: Configuração personalizada ou sugestões
    """
    await ctx.debug(f"Configurando modo Synapstor personalizado para: {tema}")
    
    translator = get_translator()
    
    if personalidades_customizadas:
        try:
            # Tentar parsear personalidades customizadas
            custom_personas = json.loads(personalidades_customizadas)
            return f"✅ Configuração customizada aplicada com {len(custom_personas)} personalidades personalizadas."
        except json.JSONDecodeError:
            return "❌ Erro: Formato JSON inválido para personalidades customizadas."
    
    # Construir resposta traduzida
    config_text = f"{translator.translate('modo_synapstor.config.title', theme=tema)}\n\n"
    config_text += f"{translator.translate('modo_synapstor.config.dynamic_approach')}\n\n"
    config_text += f"{translator.translate('modo_synapstor.config.configurable_parameters')}\n"
    
    for param in translator.translate('modo_synapstor.config.parameters'):
        config_text += f"{param}\n"
    
    config_text += f"\n{translator.translate('modo_synapstor.config.custom_personalities')}\n"
    config_text += f"{translator.translate('modo_synapstor.config.json_example', theme=tema)}\n\n"
    config_text += f"{translator.translate('modo_synapstor.config.advanced_usage')}\n"
    config_text += f"{translator.translate('modo_synapstor.config.usage_example', theme=tema)}\n\n"
    config_text += f"{translator.translate('modo_synapstor.config.advantage', theme=tema)}"
    
    return config_text


#############################################################################
# SECTION 7: FUNÇÃO DE REGISTRO (OBRIGATÓRIA)                              #
#############################################################################

# Variável global para armazenar referência do servidor
_server_instance = None

def setup_tools(server) -> List[str]:
    """
    Registra as ferramentas fornecidas por este plugin.
    
    Esta função é chamada automaticamente pelo Synapstor durante a inicialização.
    Todas as ferramentas DEVEM ser registradas aqui para ficarem disponíveis.
    
    Args:
        server: Instância do QdrantMCPServer.
    
    Returns:
        List[str]: Lista com os nomes das ferramentas registradas.
    """
    global _server_instance
    _server_instance = server
    
    logger.info("Registrando ferramentas do Modo Synapstor")
    
    translator = get_translator()
    
    # Registrar ferramenta principal
    server.add_tool(
        modo_synapstor,
        name="modo-synapstor",
        description=translator.translate("modo_synapstor.description")
    )
    
    # Registrar ferramentas auxiliares
    server.add_tool(
        info_modo_synapstor,
        name="info-modo-synapstor",
        description="Fornece informações sobre como o modo Synapstor funciona com geração dinâmica de personalidades."
    )
    
    server.add_tool(
        configurar_synapstor,
        name="configurar-synapstor", 
        description="Permite configuração personalizada do modo Synapstor com personalidades customizadas."
    )
    
    # IMPORTANTE: Retornar lista com os nomes de todas as ferramentas registradas
    return ["modo-synapstor", "info-modo-synapstor", "configurar-synapstor"]