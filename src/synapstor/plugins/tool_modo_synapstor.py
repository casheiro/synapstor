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
    
    PROMPT_GERADOR_PERSONALIDADES = """Você é um especialista em criar personalidades para debates multidisciplinares.

TEMA: {tema}

INSTRUÇÕES:
Crie exatamente {num_personalidades} personalidades especializadas que seriam as mais adequadas para debater sobre "{tema}". 

Para cada personalidade, forneça:
- Nome (pode ser pessoa real histórica/contemporânea ou arquétipo profissional)
- Expertise (área específica de conhecimento)
- Papel (função no debate)
- Estilo (tom de comunicação)
- Perspectiva (ângulo único de análise)

CRITÉRIOS:
- Personalidades devem ser complementares, não redundantes
- Cubram diferentes aspectos/dimensões do tema
- Incluam mix de perspectivas teóricas e práticas
- Considerem aspectos técnicos, éticos, sociais e econômicos quando relevante
- Sejam especialistas reconhecidos ou arquétipos profissionais relevantes

FORMATO DE RESPOSTA (JSON):
[
  {
    "nome": "Nome da Personalidade",
    "expertise": "Área específica de conhecimento",
    "papel": "Função no debate",
    "estilo": "Tom de comunicação",
    "perspectiva": "Ângulo único de análise"
  }
]

Responda apenas com o JSON válido, sem texto adicional."""

    @classmethod
    def gerar_prompt_personalidades(cls, tema: str, num_personalidades: int) -> str:
        """
        Gera o prompt para o LLM criar personalidades dinamicamente.
        """
        return cls.PROMPT_GERADOR_PERSONALIDADES.format(
            tema=tema,
            num_personalidades=num_personalidades
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
    
    TEMPLATE_PROMPT_DINAMICO = """Modo Synapstor ativado - Raciocínio Multidisciplinar com RAG.

🧠 Tema: {tema}

📚 Contexto recuperado via Qdrant:
{contexto_qdrant}

🎭 PRIMEIRA FASE - Geração de Personalidades:
{prompt_personalidades}

🎯 SEGUNDA FASE - Instruções para o Debate:

Após gerar as personalidades na PRIMEIRA FASE, proceda com o debate multidisciplinar:

1. **Apresentação das Personalidades**: Cada personalidade se apresenta brevemente (nome, expertise, perspectiva única)

2. **Análise Multidisciplinar**: Cada personalidade analisa o tema "{tema}" sob sua ótica especializada:
   - Use o contexto RAG recuperado como base factual
   - Explore diferentes dimensões do tema
   - Identifique pontos de convergência e divergência
   - Referencie evidências específicas dos documentos

3. **Debate Colaborativo**: 
   - Personalidades interagem entre si
   - Questionam e complementam perspectivas umas das outras
   - Constroem sobre as ideias apresentadas
   - Mantêm foco no tema central

4. **Síntese Multidisciplinar**: Ao final, destaque:
   - Consensos emergentes entre as personalidades
   - Tensões produtivas e diferentes abordagens
   - Implicações práticas e teóricas do tema
   - Recomendações ou próximos passos

📝 Metadados da Sessão:
- Gerado em: {timestamp}
- Documentos RAG consultados: {num_documentos}
- Personalidades solicitadas: {num_personalidades}

🚀 EXECUTE AS DUAS FASES SEQUENCIALMENTE PARA CRIAR O DEBATE MULTIDISCIPLINAR SOBRE "{tema}"."""

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
        
        # Construir prompt final
        return cls.TEMPLATE_PROMPT_DINAMICO.format(
            tema=tema,
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
        if not contexto.documentos:
            return "⚠️ Nenhum contexto específico encontrado no banco de conhecimento. O debate baseará-se no conhecimento geral das personalidades."
        
        contexto_str = f"📊 Total de documentos relevantes encontrados: {contexto.total_encontrados}\n\n"
        
        for i, doc in enumerate(contexto.documentos, 1):
            metadata = doc.get("metadata", {})
            projeto = metadata.get("projeto", "")
            arquivo = metadata.get("nome_arquivo", "")
            
            fonte = f" (Fonte: {projeto}/{arquivo})" if projeto or arquivo else ""
            contexto_str += f"📄 Documento {i}{fonte}:\n{doc['conteudo'][:500]}{'...' if len(doc['conteudo']) > 500 else ''}\n\n"
        
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
    await ctx.debug(f"Iniciando modo Synapstor para tema: {tema}")
    
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
        await ctx.debug("Consultando contexto RAG no Qdrant...")
        contexto_rag = await consultor_rag.consultar_contexto(tema, configuracao)
        
        # Construir prompt final com geração dinâmica de personalidades
        await ctx.debug(f"Construindo prompt com {max_personalidades} personalidades dinâmicas")
        
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
        
        await ctx.debug("Prompt do modo Synapstor construído com sucesso")
        return prompt_final
        
    except Exception as e:
        error_msg = f"Erro no modo Synapstor: {str(e)}"
        await ctx.debug(error_msg)
        logger.error(error_msg)
        
        # Retornar prompt de fallback
        return f"""Modo Synapstor - Erro na Inicialização

❌ Ocorreu um erro ao configurar o modo Synapstor: {str(e)}

🔄 Modo Fallback Ativado:

🧠 Tema: {tema}

👥 Personalidades (Modo Básico):
- **Especialista Técnico** – Análise técnica e implementação
- **Pensador Estratégico** – Visão macro e planejamento
- **Crítico Analítico** – Questionamento e validação

💭 Instruções Básicas:
Mesmo sem acesso ao contexto RAG completo, as personalidades devem debater o tema "{tema}" 
baseando-se em conhecimento geral e melhores práticas. Inicie o debate com cada personalidade 
apresentando sua perspectiva inicial.
"""


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
    
    return [
        "🧠 Como funciona o Modo Synapstor:",
        "",
        "1. **Geração Dinâmica de Personalidades**:",
        "   • O LLM analisa o tema fornecido",
        "   • Cria especialistas apropriados automaticamente", 
        "   • Garante perspectivas complementares e diversas",
        "",
        "2. **Recuperação de Contexto (RAG)**:",
        "   • Consulta automática ao banco Qdrant",
        "   • Recupera documentos relevantes ao tema",
        "   • Fornece base factual para o debate",
        "",
        "3. **Debate Multidisciplinar**:",
        "   • Personalidades se apresentam",
        "   • Cada uma analisa o tema sob sua ótica",
        "   • Interagem e debatem colaborativamente",
        "   • Chegam a sínteses e recomendações",
        "",
        "🎯 Vantagens da Abordagem Dinâmica:",
        "   • Adaptação total ao tema específico",
        "   • Não limitado a domínios pré-definidos",
        "   • Personalidades sempre relevantes",
        "   • Flexibilidade máxima de perspectivas",
        "",
        "💡 Exemplos de uso:",
        '   • modo-synapstor tema="Sustentabilidade em Startups"',
        '   • modo-synapstor tema="Ética em IA Generativa" max_personalidades=5',
        '   • modo-synapstor tema="Design de APIs RESTful" limite_documentos=8'
    ]


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
    
    if personalidades_customizadas:
        try:
            # Tentar parsear personalidades customizadas
            custom_personas = json.loads(personalidades_customizadas)
            return f"✅ Configuração customizada aplicada com {len(custom_personas)} personalidades personalizadas."
        except json.JSONDecodeError:
            return "❌ Erro: Formato JSON inválido para personalidades customizadas."
    
    # Retornar informações sobre configuração dinâmica
    return f"""🎛️ Configuração do Modo Synapstor para "{tema}":

🧠 **Abordagem Dinâmica**:
O Modo Synapstor agora gera personalidades automaticamente baseado no tema específico, garantindo máxima relevância e adaptabilidade.

⚙️ **Parâmetros Configuráveis**:
• max_personalidades: Número de especialistas (padrão: 4)
• limite_documentos: Documentos RAG a recuperar (padrão: 5)
• namespace: Coleção Qdrant para consulta
• incluir_contexto_debug: Informações técnicas detalhadas

🎯 **Para usar personalidades específicas**, forneça um JSON no formato:
```json
[
  {{
    "nome": "Especialista em {tema}",
    "expertise": "Área específica de conhecimento",
    "papel": "Função no debate",
    "estilo": "Tom de comunicação",
    "perspectiva": "Ângulo único de análise"
  }}
]
```

💡 **Exemplo de uso avançado**:
```
modo-synapstor tema="{tema}" max_personalidades=5 limite_documentos=8 incluir_contexto_debug=true
```

🚀 **Vantagem**: As personalidades serão geradas dinamicamente pelo LLM para se adequarem perfeitamente ao tema "{tema}", resultando em um debate mais rico e contextualizado."""


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
    
    # Registrar ferramenta principal
    server.add_tool(
        modo_synapstor,
        name="modo-synapstor",
        description="Ativa o modo Synapstor - sistema de raciocínio multidisciplinar com múltiplas personalidades especializadas e recuperação automática de contexto via RAG do banco Qdrant."
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