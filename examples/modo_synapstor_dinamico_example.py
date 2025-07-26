#!/usr/bin/env python3
"""
Exemplo de uso do Modo Synapstor Dinâmico

Este arquivo demonstra como o Synapstor (servidor MCP) fornece prompts 
estruturados que instruem o LLM cliente a executar raciocínio multidisciplinar
com geração dinâmica de personalidades especializadas.

ARQUITETURA:
- Synapstor (MCP Server): Recupera contexto RAG + constrói prompts estruturados
- LLM Cliente: Recebe prompt + executa geração de personalidades + debate
"""

def exemplo_prompt_gerado():
    """
    Exemplo do prompt estruturado que o Synapstor fornece ao LLM cliente.
    O LLM recebe este prompt e executa as instruções para realizar o debate.
    """
    print("🎭 Prompt Estruturado Fornecido pelo Synapstor ao LLM Cliente\n")
    print("="*80)
    
    prompt_exemplo = """Modo Synapstor ativado - Raciocínio Multidisciplinar com RAG.

🧠 Tema: Sustentabilidade em Startups de Tecnologia

📚 Contexto recuperado via Qdrant:
📊 Total de documentos relevantes encontrados: 4

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

🎭 PRIMEIRA FASE - Geração de Personalidades:

Você é um especialista em criar personalidades para debates multidisciplinares.

TEMA: Sustentabilidade em Startups de Tecnologia

INSTRUÇÕES:
Crie exatamente 4 personalidades especializadas que seriam as mais adequadas para debater sobre "Sustentabilidade em Startups de Tecnologia". 

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

Responda apenas com o JSON válido, sem texto adicional.

🎯 SEGUNDA FASE - Instruções para o Debate:

Após gerar as personalidades na PRIMEIRA FASE, proceda com o debate multidisciplinar:

1. **Apresentação das Personalidades**: Cada personalidade se apresenta brevemente (nome, expertise, perspectiva única)

2. **Análise Multidisciplinar**: Cada personalidade analisa o tema "Sustentabilidade em Startups de Tecnologia" sob sua ótica especializada:
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
- Gerado em: 2025-01-25 14:30:15
- Documentos RAG consultados: 4
- Personalidades solicitadas: 4

🚀 EXECUTE AS DUAS FASES SEQUENCIALMENTE PARA CRIAR O DEBATE MULTIDISCIPLINAR SOBRE "Sustentabilidade em Startups de Tecnologia"."""

    print(prompt_exemplo)
    print("="*80)


def exemplo_resposta_esperada():
    """
    Exemplo de como o LLM cliente responderia ao prompt estruturado do Synapstor.
    Esta é a execução completa que o LLM faria seguindo as instruções.
    """
    print("\n🤖 Exemplo de Execução do LLM Cliente\n")
    print("="*80)
    
    resposta_exemplo = """**PRIMEIRA FASE - Personalidades Geradas:**

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

    print(resposta_exemplo)
    print("="*80)


def arquitetura_mcp_synapstor():
    """
    Explica a arquitetura MCP e o papel do Synapstor vs LLM.
    """
    print("\n🏗️ Arquitetura MCP - Synapstor vs LLM\n")
    
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
    
    exemplo_prompt_gerado()
    exemplo_resposta_esperada()
    arquitetura_mcp_synapstor()
    
    print("\n✨ Vantagens da Arquitetura MCP:")
    print("   🎯 Synapstor fornece contexto RAG especializado")
    print("   🧠 LLM executa raciocínio multidisciplinar")
    print("   🔄 Adaptabilidade total a qualquer tema")
    print("   🚀 Qualidade superior por instruções estruturadas")
    print("   ⚡ Separação clara de responsabilidades")
    print("\n💡 Synapstor é a ponte inteligente entre dados e raciocínio!")