"""
Synapstor Mode Plugin - Multidisciplinary Reasoning System with RAG

This plugin implements synapstor_mode, which activates a multidisciplinary
reasoning system based on multiple specialized personalities that debate
collaboratively, using automatic context retrieval via RAG from Qdrant database.
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
# SECTION 1: DATA STRUCTURES                                                #
#############################################################################

# NOTE: Personality as dataclass was removed.
# Custom personalities are provided directly as JSON.
# Example JSON for custom personalities:
# [
#   {
#     "name": "Expert Name",
#     "expertise": "Knowledge area",
#     "role": "Function in debate",
#     "style": "Communication tone",
#     "perspective": "Analysis angle"
#   }
# ]


@dataclass
class RAGContext:
    """
    Represents the context retrieved via RAG from Qdrant.
    """

    documents: List[Dict[str, Any]]
    original_query: str
    total_found: int
    minimum_relevance: float = 0.0


@dataclass
class DebateConfiguration:
    """
    Configuration for multidisciplinary debate mode.
    """

    max_personalities: int = 5
    min_personalities: int = 3
    rag_documents_limit: int = 5
    default_namespace: str = "active_projects"
    minimum_relevance: float = 0.3


#############################################################################
# SECTION 2: DYNAMIC PERSONALITY GENERATOR                                  #
#############################################################################


class PersonalityGenerator:
    """
    Generates specialized personalities dynamically through LLM instructions.
    """

    @classmethod
    def _get_personality_generator_prompt(cls) -> str:
        """Gets the translated personality generator prompt."""
        translator = get_translator()
        return translator.translate("modo_synapstor.personality_generator.instruction")

    @classmethod
    def generate_personalities_prompt(cls, theme: str, num_personalities: int) -> str:
        """
        Generates the prompt for the LLM to create personalities dynamically.
        """
        prompt_template = cls._get_personality_generator_prompt()
        return prompt_template.format(theme=theme, num_personalities=num_personalities)


#############################################################################
# SECTION 3: RAG QUERY TO QDRANT                                            #
#############################################################################


class RAGConsultant:
    """
    Responsible for RAG queries to Qdrant database.
    """

    def __init__(self, qdrant_connector):
        """
        Initializes the RAG consultant with Qdrant connector.
        """
        self.qdrant_connector = qdrant_connector

    async def query_context(
        self,
        theme: str,
        configuration: DebateConfiguration,
        filters: Optional[Dict[str, Any]] = None,
    ) -> RAGContext:
        """
        Queries Qdrant to retrieve relevant context about the theme.
        """
        try:
            # Prepare improved query based on theme
            expanded_query = self._expand_query(theme)

            # Perform search in Qdrant
            results = await self.qdrant_connector.search(
                query=expanded_query,
                limit=configuration.rag_documents_limit,
                collection_name=configuration.default_namespace,
            )

            # Process results
            processed_documents = []
            for entry in results:
                processed_doc = {
                    "content": entry.content,
                    "metadata": entry.metadata or {},
                    "relevance": 1.0,  # Qdrant doesn't return score by default in FastMCP
                }
                processed_documents.append(processed_doc)

            return RAGContext(
                documents=processed_documents,
                original_query=theme,
                total_found=len(processed_documents),
                minimum_relevance=configuration.minimum_relevance,
            )

        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            # Return empty context in case of error
            return RAGContext(
                documents=[],
                original_query=theme,
                total_found=0,
                minimum_relevance=configuration.minimum_relevance,
            )

    def _expand_query(self, theme: str) -> str:
        """
        Expands the theme query with related terms for better retrieval.
        """
        # Add basic semantic context
        expansions = [
            f"concepts about {theme}",
            f"aspects of {theme}",
            f"characteristics of {theme}",
            f"principles of {theme}",
            theme,  # Original query
        ]

        # Return original query with additional context
        return f"{theme} - {' '.join(expansions[:2])}"


#############################################################################
# SECTION 4: PROMPT BUILDER                                                 #
#############################################################################


class PromptBuilder:
    """
    Builds the final Synapstor mode prompt with dynamic personality generation.
    """

    @classmethod
    def _build_dynamic_template(cls, theme: str) -> str:
        """Builds the translated dynamic template."""
        translator = get_translator()

        template = f"""{translator.translate("modo_synapstor.title")}

🧠 {translator.translate("modo_synapstor.theme", theme=theme)}

📚 {translator.translate("modo_synapstor.context_header")}
{{qdrant_context}}

🎭 {translator.translate("modo_synapstor.phase1_title")}
{{personalities_prompt}}

🎯 {translator.translate("modo_synapstor.phase2_title")}

{translator.translate("modo_synapstor.phase2_presentation")}

{translator.translate("modo_synapstor.phase2_analysis", theme=theme)}
"""

        # Add analysis bullets
        for bullet in translator.translate("modo_synapstor.phase2_analysis_bullets"):
            template += f"   - {bullet}\n"

        template += f"""
{translator.translate("modo_synapstor.phase2_debate")}
"""

        # Add debate bullets
        for bullet in translator.translate("modo_synapstor.phase2_debate_bullets"):
            template += f"   - {bullet}\n"

        template += f"""
{translator.translate("modo_synapstor.phase2_synthesis")}
"""

        # Add synthesis bullets
        for bullet in translator.translate("modo_synapstor.phase2_synthesis_bullets"):
            template += f"   - {bullet}\n"

        template += f"""
📝 {translator.translate("modo_synapstor.metadata_title")}
- {translator.translate("modo_synapstor.metadata_generated", timestamp="{{timestamp}}")}
- {translator.translate("modo_synapstor.metadata_documents", count="{{num_documents}}")}
- {translator.translate("modo_synapstor.metadata_personalities", count="{{num_personalities}}")}

🚀 {translator.translate("modo_synapstor.execute_instruction", theme=theme)}"""

        return template

    @classmethod
    def build_dynamic_prompt(
        cls, theme: str, num_personalities: int, rag_context: RAGContext
    ) -> str:
        """
        Builds the final Synapstor mode prompt with dynamic personality generation.
        """
        # Format Qdrant context
        formatted_context = cls._format_qdrant_context(rag_context)

        # Generate prompt for personality creation
        personalities_prompt = PersonalityGenerator.generate_personalities_prompt(
            theme=theme, num_personalities=num_personalities
        )

        # Build translated dynamic template
        template = cls._build_dynamic_template(theme)

        # Build final prompt
        return template.format(
            qdrant_context=formatted_context,
            personalities_prompt=personalities_prompt,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            num_documents=rag_context.total_found,
            num_personalities=num_personalities,
        )

    @classmethod
    def _format_qdrant_context(cls, context: RAGContext) -> str:
        """
        Formats the context retrieved from Qdrant.
        """
        translator = get_translator()

        if not context.documents:
            return translator.translate("modo_synapstor.no_context")

        context_str = f"📊 {translator.translate('modo_synapstor.total_documents', count=context.total_found)}\n\n"

        for i, doc in enumerate(context.documents, 1):
            metadata = doc.get("metadata", {})
            project = metadata.get("project", "") or metadata.get("projeto", "")
            filename = metadata.get("filename", "") or metadata.get("nome_arquivo", "")

            source = (
                f" {translator.translate('modo_synapstor.source_prefix', source=f'{project}/{filename}')}"
                if project or filename
                else ""
            )
            context_str += f"📄 {translator.translate('modo_synapstor.document_prefix', number=i)}{source}:\n{doc['content'][:500]}{'...' if len(doc['content']) > 500 else ''}\n\n"

        return context_str.strip()


#############################################################################
# SECTION 5: MAIN TOOL                                                      #
#############################################################################


async def synapstor_mode(
    ctx: Context,
    theme: str,
    max_personalities: int = 4,
    document_limit: int = 5,
    namespace: str = "",
    include_debug_context: bool = False,
) -> str:
    """
    Activates Synapstor mode - multidisciplinary reasoning system with RAG.

    This MCP tool builds a structured prompt that instructs the LLM client to:
    1) Generate specialized personalities dynamically based on the theme
    2) Execute a multidisciplinary debate using RAG context retrieved from Qdrant
    3) Produce multifaceted analysis with complementary perspectives

    Synapstor provides RAG context and instructions; the LLM executes the reasoning.

    :param ctx: MCP request context
    :param theme: Main theme for multidisciplinary analysis
    :param max_personalities: Number of experts to be generated (default: 4)
    :param document_limit: Limit of RAG documents to retrieve (default: 5)
    :param namespace: Qdrant namespace/collection for search (default: uses server config)
    :param include_debug_context: Whether to include technical debug information
    :return: Structured prompt that instructs the LLM to execute Synapstor mode
    """
    translator = get_translator()
    await ctx.debug(translator.translate("modo_synapstor.debug.starting", theme=theme))

    try:
        # Use server default namespace if not specified
        final_namespace = (
            namespace or _server_instance.qdrant_settings.collection_name or "synapstor"
        )

        # Debate configuration
        configuration = DebateConfiguration(
            max_personalities=max_personalities,
            rag_documents_limit=document_limit,
            default_namespace=final_namespace,
        )

        # Access Qdrant connector through server global reference
        # This reference will be defined in setup_tools function
        qdrant_connector = _server_instance.qdrant_connector

        # Initialize RAG consultant
        rag_consultant = RAGConsultant(qdrant_connector)

        # Retrieve context via RAG
        await ctx.debug(translator.translate("modo_synapstor.debug.consulting_rag"))
        rag_context = await rag_consultant.query_context(theme, configuration)

        # Build final prompt with dynamic personality generation
        await ctx.debug(
            translator.translate(
                "modo_synapstor.debug.building_prompt", count=max_personalities
            )
        )

        final_prompt = PromptBuilder.build_dynamic_prompt(
            theme=theme, num_personalities=max_personalities, rag_context=rag_context
        )

        # Add debug context if requested
        if include_debug_context:
            debug_info = "\n\n🔧 Debug Info:\n"
            debug_info += f"- Configuration: {asdict(configuration)}\n"
            debug_info += f"- Requested personalities: {max_personalities}\n"
            debug_info += f"- RAG documents found: {rag_context.total_found}\n"
            debug_info += f"- Namespace used: {final_namespace}\n"
            final_prompt += debug_info

        await ctx.debug(translator.translate("modo_synapstor.debug.success"))
        return final_prompt

    except Exception as e:
        error_msg = f"Error in Synapstor mode: {str(e)}"
        await ctx.debug(error_msg)
        logger.error(error_msg)

        # Return translated fallback prompt
        fallback_prompt = f"""{translator.translate("modo_synapstor.errors.initialization")}

{translator.translate("modo_synapstor.errors.error_occurred", error=str(e))}

{translator.translate("modo_synapstor.errors.fallback_activated")}

🧠 {translator.translate("modo_synapstor.theme", theme=theme)}

{translator.translate("modo_synapstor.errors.fallback_personalities")}
- {translator.translate("modo_synapstor.errors.technical_expert")}
- {translator.translate("modo_synapstor.errors.strategic_thinker")}
- {translator.translate("modo_synapstor.errors.analytical_critic")}

{translator.translate("modo_synapstor.errors.fallback_instructions", theme=theme)}
"""
        return fallback_prompt


#############################################################################
# SECTION 6: AUXILIARY TOOLS                                                #
#############################################################################


async def synapstor_mode_info(ctx: Context) -> List[str]:
    """
    Provides information about how Synapstor mode works.

    :param ctx: MCP request context
    :return: Information about Synapstor mode functioning
    """
    await ctx.debug("Providing information about Synapstor mode")

    translator = get_translator()

    info_lines = [
        translator.translate("modo_synapstor.info.title"),
        "",
        translator.translate("modo_synapstor.info.dynamic_generation"),
    ]

    for bullet in translator.translate("modo_synapstor.info.dynamic_bullets"):
        info_lines.append(f"   {bullet}")

    info_lines.extend(
        [
            "",
            translator.translate("modo_synapstor.info.rag_retrieval"),
        ]
    )

    for bullet in translator.translate("modo_synapstor.info.rag_bullets"):
        info_lines.append(f"   {bullet}")

    info_lines.extend(
        [
            "",
            translator.translate("modo_synapstor.info.debate"),
        ]
    )

    for bullet in translator.translate("modo_synapstor.info.debate_bullets"):
        info_lines.append(f"   {bullet}")

    info_lines.extend(
        [
            "",
            translator.translate("modo_synapstor.info.advantages_title"),
        ]
    )

    for advantage in translator.translate("modo_synapstor.info.advantages"):
        info_lines.append(f"   {advantage}")

    info_lines.extend(
        [
            "",
            translator.translate("modo_synapstor.info.examples_title"),
        ]
    )

    for example in translator.translate("modo_synapstor.info.examples"):
        info_lines.append(f"   {example}")

    return info_lines


async def configure_synapstor(
    ctx: Context, theme: str, custom_personalities: Optional[str] = None
) -> str:
    """
    Allows custom configuration of Synapstor mode.

    :param ctx: MCP request context
    :param theme: Theme for analysis
    :param custom_personalities: JSON with custom personalities
    :return: Custom configuration or suggestions
    """
    await ctx.debug(f"Configuring custom Synapstor mode for: {theme}")

    translator = get_translator()

    if custom_personalities:
        try:
            # Try to parse custom personalities
            custom_personas = json.loads(custom_personalities)
            return f"✅ Custom configuration applied with {len(custom_personas)} personalized personalities."
        except json.JSONDecodeError:
            return "❌ Error: Invalid JSON format for custom personalities."

    # Build translated response
    config_text = (
        f"{translator.translate('modo_synapstor.config.title', theme=theme)}\n\n"
    )
    config_text += (
        f"{translator.translate('modo_synapstor.config.dynamic_approach')}\n\n"
    )
    config_text += (
        f"{translator.translate('modo_synapstor.config.configurable_parameters')}\n"
    )

    for param in translator.translate("modo_synapstor.config.parameters"):
        config_text += f"{param}\n"

    config_text += (
        f"\n{translator.translate('modo_synapstor.config.custom_personalities')}\n"
    )
    config_text += (
        f"{translator.translate('modo_synapstor.config.json_example', theme=theme)}\n\n"
    )
    config_text += f"{translator.translate('modo_synapstor.config.advanced_usage')}\n"
    config_text += f"{translator.translate('modo_synapstor.config.usage_example', theme=theme)}\n\n"
    config_text += (
        f"{translator.translate('modo_synapstor.config.advantage', theme=theme)}"
    )

    return config_text


#############################################################################
# SECTION 7: REGISTRATION FUNCTION (REQUIRED)                              #
#############################################################################

# Global variable to store server reference
_server_instance = None


def setup_tools(server) -> List[str]:
    """
    Registers the tools provided by this plugin.

    This function is called automatically by Synapstor during initialization.
    All tools MUST be registered here to be available.

    Args:
        server: QdrantMCPServer instance.

    Returns:
        List[str]: List with the names of registered tools.
    """
    global _server_instance
    _server_instance = server

    logger.info("Registering Synapstor Mode tools")

    translator = get_translator()

    # Register main tool
    server.add_tool(
        synapstor_mode,
        name="modo-synapstor",
        description=translator.translate("modo_synapstor.description"),
    )

    # Register auxiliary tools
    server.add_tool(
        synapstor_mode_info,
        name="info-modo-synapstor",
        description="Provides information about how Synapstor mode works with dynamic personality generation.",
    )

    server.add_tool(
        configure_synapstor,
        name="configurar-synapstor",
        description="Allows custom configuration of Synapstor mode with custom personalities.",
    )

    # IMPORTANT: Return list with the names of all registered tools
    return ["modo-synapstor", "info-modo-synapstor", "configurar-synapstor"]
