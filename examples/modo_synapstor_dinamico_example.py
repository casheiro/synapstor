#!/usr/bin/env python3
"""
Dynamic Synapstor Mode Usage Example

This file demonstrates how Synapstor (MCP server) provides structured 
prompts that instruct the LLM client to execute multidisciplinary reasoning
with dynamic generation of specialized personalities.

ARCHITECTURE:
- Synapstor (MCP Server): Retrieves RAG context + builds structured prompts
- LLM Client: Receives prompt + executes personality generation + debate
"""

def generated_prompt_example():
    """
    Example of the structured prompt that Synapstor provides to the LLM client.
    The LLM receives this prompt and executes the instructions to conduct the debate.
    """
    print("🎭 Structured Prompt Provided by Synapstor to LLM Client\n")
    print("="*80)
    
    prompt_example = """Synapstor Mode activated - Multidisciplinary Reasoning with RAG.

🧠 Theme: Sustainability in Technology Startups

📚 Context retrieved via Qdrant:
📊 Total relevant documents found: 4

📄 Documento 1 (Fonte: sustentabilidade_tech/green_coding.md):
Green coding practices podem reduzir o consumo energético de aplicações em até 30%. 
Técnicas incluem otimização de algoritmos, uso eficiente de recursos de cloud e 
práticas de desenvolvimento sustentável...

📄 Documento 2 (Fonte: startups_cases/patagonia_tech.md):
Patagonia utiliza tecnologia para rastrear pegada de carbono em toda cadeia produtiva.
Blockchain para transparência, IoT para monitoramento ambiental e IA para otimização
de recursos são pilares da estratégia sustentável...

📄 Documento 3 (Fonte: investimentos/esg_venture.md):
Critérios ESG (Environmental, Social, Governance) se tornaram fundamentais para 
captação de investimento. VCs avaliam não apenas retorno financeiro mas também
impacto socioambiental das startups...

🎭 FIRST PHASE - Personality Generation:

You are an expert in creating personalities for multidisciplinary debates.

THEME: Sustainability in Technology Startups

INSTRUCTIONS:
Create exactly 4 specialized personalities that would be most suitable for debating "Sustainability in Technology Startups". 

For each personality, provide:
- Name (can be real historical/contemporary person or professional archetype)
- Expertise (specific area of knowledge)
- Role (function in debate)
- Style (communication tone)
- Perspective (unique angle of analysis)

CRITERIA:
- Personalities should be complementary, not redundant
- Cover different aspects/dimensions of the theme
- Include mix of theoretical and practical perspectives
- Consider technical, ethical, social and economic aspects when relevant
- Be recognized experts or relevant professional archetypes

RESPONSE FORMAT (JSON):
[
  {
    "name": "Personality Name",
    "expertise": "Specific area of knowledge",
    "role": "Function in debate",
    "style": "Communication tone",
    "perspective": "Unique angle of analysis"
  }
]

Respond only with valid JSON, no additional text.

🎯 SECOND PHASE - Debate Instructions:

After generating personalities in the FIRST PHASE, proceed with multidisciplinary debate:

1. **Personality Presentation**: Each personality briefly introduces themselves (name, expertise, unique perspective)

2. **Multidisciplinary Analysis**: Each personality analyzes the theme "Sustainability in Technology Startups" from their specialized perspective:
   - Use the retrieved RAG context as factual basis
   - Explore different dimensions of the theme
   - Identify convergence and divergence points
   - Reference specific evidence from documents

3. **Collaborative Debate**: 
   - Personalities interact with each other
   - Question and complement each other's perspectives
   - Build upon presented ideas
   - Maintain focus on central theme

4. **Multidisciplinary Synthesis**: At the end, highlight:
   - Emerging consensus among personalities
   - Productive tensions and different approaches
   - Practical and theoretical implications of the theme
   - Recommendations or next steps

📝 Session Metadata:
- Generated at: 2025-01-25 14:30:15
- RAG documents consulted: 4
- Requested personalities: 4

🚀 EXECUTE BOTH PHASES SEQUENTIALLY TO CREATE THE MULTIDISCIPLINARY DEBATE ON "Sustainability in Technology Startups".""""""    print(prompt_example)
    print("="*80)

    print(prompt_example)
    print("="*80)


def expected_response_example():
    """
    Example of how the LLM client would respond to Synapstor's structured prompt.
    This is the complete execution the LLM would perform following the instructions.
    """
    print("\n🤖 Example of LLM Client Execution\n")
    print("="*80)
    
    response_example = """**FIRST PHASE - Generated Personalities:**

[
  {
    "nome": "Dr. John Elkington",
    "expertise": "Sustentabilidade Corporativa e Triple Bottom Line",
    "papel": "Estrategista ESG",
    "estilo": "visionário-pragmático",
    "perspectiva": "sustentabilidade como vantagem competitiva"
  },
  {
    "nome": "Rana Foroohar",
    "expertise": "Economia Sustentável e Tecnologia",
    "papel": "Analista de Impacto Econômico",
    "estilo": "jornalístico-analítico",
    "perspectiva": "macroeconomia da sustentabilidade"
  },
  {
    "nome": "Arquiteto de Software Verde",
    "expertise": "Green Computing e Otimização Energética",
    "papel": "Especialista em Implementação Técnica",
    "estilo": "técnico-objetivo",
    "perspectiva": "eficiência de recursos computacionais"
  },
  {
    "nome": "Sarah Chen (VC Partner)",
    "expertise": "Venture Capital e Impacto Social",
    "papel": "Investidora de Impacto",
    "estilo": "empreendedor-orientado",
    "perspectiva": "viabilidade financeira de negócios sustentáveis"
  }
]

**SEGUNDA FASE - Debate Multidisciplinar:**

**Dr. John Elkington:** "Olá, sou John Elkington, e há décadas trabalho com sustentabilidade corporativa. O conceito de Triple Bottom Line - Pessoas, Planeta e Lucro - nunca foi tão relevante para startups de tecnologia. Vejo no documento da Patagonia um exemplo perfeito de como a tecnologia pode ser usada para transparência total na cadeia de suprimentos."

**Rana Foroohar:** "Rana Foroohar aqui, especialista em economia tecnológica. O que me chama atenção nos dados RAG é como os critérios ESG estão realmente mudando o jogo para captação de recursos. Não é mais 'nice to have', é fundamental para sobrevivência no mercado."

**Arquiteto de Software Verde:** "Como arquiteto focado em green computing, posso confirmar que o green coding mencionado nos documentos não é apenas teoria. Reduções de 30% no consumo energético são totalmente possíveis com otimizações de algoritmo e uso inteligente de cloud resources."

**Sarah Chen:** "Sarah Chen, partner em VC de impacto. O que vocês estão dizendo se alinha com o que vemos no mercado. Startups sustentáveis não apenas captam mais recursos, mas têm valuation premium. A questão é: como escalamos essas práticas sem comprometer a agilidade startup?"

**Dr. Elkington:** "Sarah levanta um ponto crucial. A tensão entre velocidade e sustentabilidade é real, mas vejo nos casos de sucesso que sustentabilidade bem implementada acelera, não desacelera. A Patagonia conseguiu isso."

**Arquiteto de Software:** "Concordo, John. Em termos técnicos, práticas de green coding frequentemente resultam em código mais eficiente e maintível. É um falso dilema pensar que sustentabilidade compromete performance."

**Rana Foroohar:** "A questão econômica é fascinante. Estamos vendo uma mudança sistêmica onde o mercado premia eficiência de recursos. As startups que entenderem isso primeiro terão vantagem competitiva significativa."

**Sarah Chen:** "Exato, Rana. E do ponto de vista de investimento, startups com métricas ESG sólidas têm menor risco de stranded assets e maior resiliência a mudanças regulatórias."

**SÍNTESE MULTIDISCIPLINAR:**

**Consensos Emergentes:**
- Sustentabilidade é vantagem competitiva, não custo adicional
- Tecnologia é habilitadora fundamental para práticas sustentáveis
- Mercado financeiro está premiando empresas ESG-compliant
- Green coding resulta em melhor performance técnica

**Tensões Produtivas:**
- Velocidade startup vs. implementação cuidadosa de práticas sustentáveis
- Métricas de curto prazo vs. impacto de longo prazo
- Custos iniciais vs. economia futura

**Recomendações:**
1. Integrar métricas de sustentabilidade desde o MVP
2. Adotar green coding como standard de desenvolvimento
3. Usar blockchain para transparência da cadeia de valor
4. Estabelecer partnerships com investidores de impacto

O debate revela que sustentabilidade em startups de tecnologia não é apenas responsabilidade social, mas imperativo estratégico para sucesso no mercado atual."""

    print(response_example)
    print("="*80)


def mcp_synapstor_architecture():
    """
    Explains MCP architecture and the role of Synapstor vs LLM.
    """
    print("\n🏗️ MCP Architecture - Synapstor vs LLM\n")
    
    print("🔧 SYNAPSTOR (MCP Server):")
    print("   • Conecta-se ao banco Qdrant")
    print("   • Recupera documentos relevantes via RAG")
    print("   • Constrói prompts estruturados")
    print("   • Fornece contexto factual ao LLM")
    print("   • Define instruções de execução")
    
    print("\n🧠 LLM (MCP Client):")
    print("   • Recebe prompt estruturado do Synapstor")
    print("   • Gera personalidades especializadas dinamicamente")
    print("   • Executa debate multidisciplinar")
    print("   • Utiliza contexto RAG fornecido")
    print("   • Produz análise final e sínteses")
    
    print("\n🔄 FLUXO DE TRABALHO:")
    print("   1. LLM solicita: modo-synapstor tema='Sustentabilidade Tech'")
    print("   2. Synapstor consulta Qdrant e recupera documentos relevantes")
    print("   3. Synapstor constrói prompt com contexto RAG + instruções")
    print("   4. LLM recebe prompt e executa as duas fases:")
    print("      • Fase 1: Gera personalidades apropriadas")
    print("      • Fase 2: Executa debate usando contexto fornecido")
    print("   5. LLM retorna análise multidisciplinar completa")
    
    print("\n🎯 Exemplos de Melhoria:")
    print("   • Tema: 'Ética em NFTs para Arte Digital'")
    print("     ANTES: Tentaria encaixar em 'tecnologia' com especialistas genéricos")
    print("     AGORA: Gera especialistas em arte digital, direitos autorais, blockchain, filosofia da arte")
    print()
    print("   • Tema: 'Psicologia de UX em Apps de Meditação'")
    print("     ANTES: Mistura confusa entre 'tecnologia' e 'geral'")
    print("     AGORA: Especialistas em UX/UI, psicologia comportamental, mindfulness, product design")


if __name__ == "__main__":
    print("🎭 Modo Synapstor - Arquitetura MCP Dinâmica")
    print("=" * 50)
    
    generated_prompt_example()
    expected_response_example()
    mcp_synapstor_architecture()
    
    print("\n✨ Vantagens da Arquitetura MCP:")
    print("   🎯 Synapstor fornece contexto RAG especializado")
    print("   🧠 LLM executa raciocínio multidisciplinar")
    print("   🔄 Adaptabilidade total a qualquer tema")
    print("   🚀 Qualidade superior por instruções estruturadas")
    print("   ⚡ Separação clara de responsabilidades")
    print("\n💡 Synapstor é a ponte inteligente entre dados e raciocínio!")