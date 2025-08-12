# Base de Conhecimento Synapstor

Este diretório contém documentação de conhecimento focada em negócio estruturada de acordo com a especificação Matrix Embedding Framework (MEF).

## Estrutura de Diretórios

```
knowledge-source-pt/
├── business/     # Regras de negócio, processos e modelos
├── product/      # Diretrizes de produto, fluxos de usuário e padrões de design
├── strategy/     # Decisões estratégicas e escolhas arquiteturais
├── culture/      # Processos de equipe, práticas culturais e diretrizes
└── technical/    # (Futuro) Padrões técnicos e detalhes de implementação
```

## Domínios de Conhecimento

### Domínio Business
Contém UKIs focadas em regras de negócio, políticas e modelos operacionais:
- Regras de validação e processamento MEF
- Modelo de negócio de integração MCP
- Políticas de indexação e armazenamento de conhecimento

### Domínio Product  
Contém UKIs focadas em experiência do usuário, design de interface e fluxos de produto:
- Diretrizes de design de interface CLI
- Padrões de experiência de busca de conhecimento
- Fluxos de trabalho de autoria de documentos MEF

### Domínio Strategy
Contém UKIs documentando decisões estratégicas e planejamento de longo prazo:
- Justificativa de adoção do protocolo MCP
- Estratégia do framework de conhecimento MEF
- Posicionamento open source e estratégia comunitária

### Domínio Culture
Contém UKIs focadas em práticas de equipe, processos e padrões culturais:
- Práticas de conventional commits e releases automatizados
- Diretrizes de desenvolvimento de internacionalização
- Padrões de contribuição open source

## Usando Esta Base de Conhecimento

### Para Desenvolvedores
Essas UKIs fornecem contexto para entender requisitos de negócio, decisões de design e diretrizes de implementação. Use-as para:
- Entender o raciocínio por trás de escolhas técnicas
- Aprender sobre regras de negócio que afetam implementação
- Seguir padrões e práticas estabelecidas

### Para Equipes de Produto
Essas UKIs documentam decisões de produto, fluxos de usuário e diretrizes de design. Use-as para:
- Manter consistência em decisões de produto
- Entender padrões de experiência do usuário
- Referenciar diretrizes de design estabelecidas

### Para Equipes de Negócio
Essas UKIs capturam regras de negócio, processos e decisões estratégicas. Use-as para:
- Entender políticas operacionais
- Referenciar justificativa estratégica para decisões
- Manter consistência em processos de negócio

### Para Contribuidores da Comunidade
Essas UKIs ajudam novos contribuidores a entender cultura, processos e padrões do projeto. Use-as para:
- Aprender diretrizes e padrões de contribuição
- Entender governança e tomada de decisão do projeto
- Referenciar práticas e fluxos de desenvolvimento

## Indexação com MEF

Para indexar esta base de conhecimento com suporte MEF do Synapstor:

```bash
# Habilitar processamento MEF
synapstor-indexer --project synapstor-conhecimento --path ./knowledge-source-pt -m

# Modo de validação rigorosa
synapstor-indexer --project synapstor-conhecimento --path ./knowledge-source-pt -m -e
```

## Mantendo Esta Base de Conhecimento

### Adicionando Novas UKIs
1. Determinar domínio apropriado (business, product, strategy, culture)
2. Seguir especificação MEF para estrutura e metadados
3. Usar IDs descritivas seguindo padrão `unik-[dominio]-[nome-descritivo]`
4. Incluir exemplos relevantes e relacionamentos
5. Validar usando ferramentas de validação MEF

### Atualizando UKIs Existentes
1. Atualizar data `last_validation` ao revisar conteúdo
2. Garantir que links `related_to` permaneçam precisos
3. Atualizar exemplos se sistemas subjacentes mudarem
4. Manter consistência com UKIs relacionadas

### Padrões de Qualidade
- Conteúdo deve ser acionável e prático
- Exemplos devem ser realistas e atuais
- Linguagem deve ser clara e acessível
- Relacionamentos devem ser significativos e mantidos

## Integração com Fluxo de Desenvolvimento

Esta base de conhecimento é projetada para ser indexada pelo Synapstor e disponibilizada para LLMs através de integração MCP, habilitando:
- Assistência contextual durante desenvolvimento
- Descoberta automatizada de regras de negócio relevantes
- Aplicação consistente de padrões estabelecidos
- Compartilhamento de conhecimento através de fronteiras de equipe

## Contribuindo

Ao contribuir para esta base de conhecimento:
1. Seguir requisitos de especificação MEF
2. Garantir que conteúdo seja focado em negócio/produto (não implementação técnica)
3. Incluir exemplos práticos e intenção de uso clara
4. Vincular a UKIs relacionadas onde apropriado
5. Atualizar datas de validação ao revisar conteúdo

Para detalhes de implementação técnica, consulte a documentação principal do Synapstor e codebase.

## Idiomas Disponíveis

- **Português (pt_BR)**: Esta base de conhecimento (knowledge-source-pt/)
- **English (en_US)**: Base de conhecimento em inglês (knowledge-source/)

Ambas as bases de conhecimento seguem a mesma estrutura MEF e cobrem os mesmos conceitos de negócio, adaptados para suas respectivas culturas e idiomas.
