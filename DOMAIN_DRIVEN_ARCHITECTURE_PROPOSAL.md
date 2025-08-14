# Proposta de Arquitetura por Domínios (Domain-Driven Design) - Synapstor

## Visão Geral

Esta proposta apresenta uma reestruturação completa do projeto Synapstor utilizando princípios de Domain-Driven Design (DDD), organizando o código em contextos limitados (bounded contexts) que refletem os domínios de negócio do sistema.

## Objetivos da Refatoração

### Problemas Identificados na Estrutura Atual
- **Mistura de responsabilidades**: Arquivos no root do pacote com responsabilidades diferentes
- **Acoplamento alto**: Dependências cruzadas entre componentes de infraestrutura e negócio
- **Falta de isolamento**: Mudanças em uma funcionalidade afetam outras
- **Configurações centralizadas**: Todas as configurações em um único arquivo
- **Plugins sem categorização**: Ferramentas MCP sem organização clara

### Benefícios da Nova Arquitetura
1. **Isolamento de domínios**: Cada contexto evolui independentemente
2. **Escalabilidade**: Facilita adição de novos domínios e funcionalidades
3. **Manutenibilidade**: Código mais organizado e fácil de entender
4. **Testabilidade**: Testes mais focados e isolados
5. **Especialização**: Times podem focar em domínios específicos
6. **Alinhamento com MEF**: Estrutura natural para Matrix Embedding Framework

## Arquitetura Proposta

### Estrutura de Diretórios Completa

```
src/synapstor/
├── __init__.py
├── domains/                      # Contextos limitados por domínio
│   ├── __init__.py
│   ├── knowledge/               # Domínio do Conhecimento
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── document.py         # Entidade Documento
│   │   │   ├── uki.py              # Unit of Knowledge Interlinked (MEF)
│   │   │   ├── knowledge_unit.py   # Unidade de Conhecimento genérica
│   │   │   └── content_metadata.py # Metadados de conteúdo
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── indexing_service.py     # Serviço de indexação
│   │   │   ├── mef_service.py          # Serviço MEF
│   │   │   ├── search_service.py       # Serviço de busca
│   │   │   └── validation_service.py   # Validação de conhecimento
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_repository.py     # Interface do repositório
│   │   │   └── knowledge_repository_impl.py # Implementação
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── embedding_vector.py     # Vetor de embedding
│   │   │   ├── search_criteria.py      # Critérios de busca
│   │   │   ├── domain_type.py          # Tipos de domínio MEF
│   │   │   └── knowledge_context.py    # Contexto do conhecimento
│   │   └── specifications/
│   │       ├── __init__.py
│   │       ├── mef_specification.py    # Especificações MEF
│   │       └── search_specification.py # Especificações de busca
│   ├── memory/                  # Domínio da Memória
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── memory.py           # Entidade Memória
│   │   │   ├── conversation.py     # Conversa/Sessão
│   │   │   ├── context.py          # Contexto de conversa
│   │   │   └── recall.py           # Recuperação de memória
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── memory_service.py       # Gerenciamento de memórias
│   │   │   ├── retrieval_service.py    # Recuperação contextual
│   │   │   ├── context_service.py      # Gerenciamento de contexto
│   │   │   └── forgetting_service.py   # Estratégias de esquecimento
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── memory_repository.py        # Interface do repositório
│   │   │   └── memory_repository_impl.py   # Implementação
│   │   └── value_objects/
│   │       ├── __init__.py
│   │       ├── memory_importance.py    # Importância da memória
│   │       ├── recall_strategy.py      # Estratégia de recuperação
│   │       └── temporal_context.py     # Contexto temporal
│   ├── embedding/               # Domínio de Embeddings
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── embedding.py        # Entidade Embedding
│   │   │   ├── model.py            # Modelo de embedding
│   │   │   ├── vector_space.py     # Espaço vetorial
│   │   │   └── similarity.py       # Cálculo de similaridade
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── embedding_service.py        # Geração de embeddings
│   │   │   ├── model_service.py            # Gerenciamento de modelos
│   │   │   ├── similarity_service.py       # Cálculo de similaridades
│   │   │   └── optimization_service.py     # Otimização de embeddings
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base_provider.py            # Provider abstrato
│   │   │   ├── fastembed_provider.py       # Provider FastEmbed
│   │   │   ├── sentence_transformer_provider.py # Provider Sentence Transformers
│   │   │   ├── openai_provider.py          # Provider OpenAI
│   │   │   └── factory.py                  # Factory de providers
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── embedding_config.py     # Configuração de embedding
│   │   │   ├── model_config.py         # Configuração de modelo
│   │   │   └── vector_dimensions.py    # Dimensões do vetor
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── model_repository.py     # Repositório de modelos
│   │       └── embedding_cache.py      # Cache de embeddings
│   └── mcp/                     # Domínio MCP (Model Context Protocol)
│       ├── __init__.py
│       ├── entities/
│       │   ├── __init__.py
│       │   ├── tool.py              # Entidade Ferramenta MCP
│       │   ├── transport.py         # Transporte MCP
│       │   ├── session.py           # Sessão MCP
│       │   └── capability.py        # Capacidade do servidor
│       ├── services/
│       │   ├── __init__.py
│       │   ├── tool_service.py          # Gerenciamento de ferramentas
│       │   ├── transport_service.py     # Gerenciamento de transportes
│       │   ├── session_service.py       # Gerenciamento de sessões
│       │   └── capability_service.py    # Gerenciamento de capacidades
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── base_tool.py             # Ferramenta base
│       │   ├── memory_tools.py          # Ferramentas de memória
│       │   ├── search_tools.py          # Ferramentas de busca
│       │   ├── boilerplate_tools.py     # Ferramentas de boilerplate
│       │   ├── changelog_tools.py       # Ferramentas de changelog
│       │   └── modo_synapstor_tools.py  # Modo Synapstor
│       ├── transports/
│       │   ├── __init__.py
│       │   ├── base_transport.py        # Transporte base
│       │   ├── stdio_transport.py       # Transporte STDIO
│       │   ├── sse_transport.py         # Transporte SSE
│       │   └── http_transport.py        # Transporte HTTP
│       └── value_objects/
│           ├── __init__.py
│           ├── tool_definition.py       # Definição de ferramenta
│           ├── transport_config.py      # Configuração de transporte
│           └── mcp_protocol.py          # Protocolo MCP
├── application/                 # Camada de aplicação cross-domain
│   ├── __init__.py
│   ├── orchestrators/           # Orquestradores de use cases complexos
│   │   ├── __init__.py
│   │   ├── project_indexer.py       # Indexação de projetos
│   │   ├── semantic_search.py       # Busca semântica
│   │   ├── modo_synapstor.py        # Modo Synapstor
│   │   └── knowledge_pipeline.py   # Pipeline de conhecimento
│   ├── use_cases/               # Use cases específicos
│   │   ├── __init__.py
│   │   ├── index_project_use_case.py    # UC: Indexar projeto
│   │   ├── search_memory_use_case.py    # UC: Buscar memória
│   │   ├── store_memory_use_case.py     # UC: Armazenar memória
│   │   ├── validate_mef_use_case.py     # UC: Validar MEF
│   │   └── generate_embeddings_use_case.py # UC: Gerar embeddings
│   ├── dto/                     # Data Transfer Objects
│   │   ├── __init__.py
│   │   ├── requests/
│   │   │   ├── __init__.py
│   │   │   ├── index_request.py     # Request de indexação
│   │   │   ├── search_request.py    # Request de busca
│   │   │   ├── memory_request.py    # Request de memória
│   │   │   └── mef_request.py       # Request MEF
│   │   └── responses/
│   │       ├── __init__.py
│   │       ├── index_response.py    # Response de indexação
│   │       ├── search_response.py   # Response de busca
│   │       ├── memory_response.py   # Response de memória
│   │       └── mef_response.py      # Response MEF
│   ├── events/                  # Sistema de eventos
│   │   ├── __init__.py
│   │   ├── base_event.py            # Evento base
│   │   ├── knowledge_events.py      # Eventos de conhecimento
│   │   ├── memory_events.py         # Eventos de memória
│   │   ├── embedding_events.py      # Eventos de embedding
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_handlers.py    # Handlers de conhecimento
│   │   │   ├── memory_handlers.py       # Handlers de memória
│   │   │   └── embedding_handlers.py    # Handlers de embedding
│   │   └── publishers/
│   │       ├── __init__.py
│   │       └── event_publisher.py   # Publicador de eventos
│   └── workflows/               # Workflows complexos
│       ├── __init__.py
│       ├── indexing_workflow.py     # Workflow de indexação
│       ├── search_workflow.py       # Workflow de busca
│       └── mef_workflow.py          # Workflow MEF
├── infrastructure/              # Infraestrutura compartilhada
│   ├── __init__.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── qdrant/
│   │   │   ├── __init__.py
│   │   │   ├── connector.py         # Conector Qdrant
│   │   │   ├── config.py            # Configuração Qdrant
│   │   │   ├── migrations.py        # Migrações Qdrant
│   │   │   └── query_builder.py     # Construtor de queries
│   │   ├── local/
│   │   │   ├── __init__.py
│   │   │   ├── file_storage.py      # Armazenamento local
│   │   │   └── index_storage.py     # Índice local
│   │   └── adapters/
│   │       ├── __init__.py
│   │       ├── knowledge_adapter.py # Adaptador conhecimento
│   │       ├── memory_adapter.py    # Adaptador memória
│   │       └── embedding_adapter.py # Adaptador embedding
│   ├── messaging/
│   │   ├── __init__.py
│   │   ├── event_bus.py             # Event bus
│   │   ├── message_broker.py        # Message broker
│   │   └── subscribers.py           # Subscribers
│   ├── serialization/
│   │   ├── __init__.py
│   │   ├── json_serializer.py       # Serialização JSON
│   │   ├── yaml_serializer.py       # Serialização YAML
│   │   ├── mef_serializer.py        # Serialização MEF
│   │   └── pickle_serializer.py     # Serialização Pickle
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── logging.py               # Sistema de logs
│   │   ├── metrics.py               # Métricas
│   │   ├── tracing.py               # Tracing
│   │   └── health_check.py          # Health checks
│   └── external/
│       ├── __init__.py
│       ├── file_processors/
│       │   ├── __init__.py
│       │   ├── text_processor.py    # Processador de texto
│       │   ├── yaml_processor.py    # Processador YAML
│       │   ├── markdown_processor.py # Processador Markdown
│       │   └── binary_processor.py  # Processador binário
│       └── apis/
│           ├── __init__.py
│           ├── openai_client.py     # Cliente OpenAI
│           └── huggingface_client.py # Cliente HuggingFace
├── presentation/                # Interfaces de usuário
│   ├── __init__.py
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── server.py                # Servidor MCP principal
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── tool_handlers.py     # Handlers de ferramentas
│   │   │   ├── resource_handlers.py # Handlers de recursos
│   │   │   └── prompt_handlers.py   # Handlers de prompts
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py   # Middleware de auth
│   │   │   ├── cors_middleware.py   # Middleware CORS
│   │   │   ├── logging_middleware.py # Middleware de log
│   │   │   └── rate_limit_middleware.py # Middleware rate limit
│   │   └── serializers/
│   │       ├── __init__.py
│   │       ├── tool_serializer.py   # Serialização de ferramentas
│   │       └── response_serializer.py # Serialização de responses
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py                  # Entry point CLI
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── base_command.py      # Comando base
│   │   │   ├── ctl_command.py       # Comando ctl
│   │   │   ├── indexer_command.py   # Comando indexer
│   │   │   ├── server_command.py    # Comando server
│   │   │   └── config_command.py    # Comando config
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   ├── indexing_controller.py # Controller indexação
│   │   │   ├── server_controller.py   # Controller servidor
│   │   │   └── config_controller.py   # Controller config
│   │   ├── templates/
│   │   │   ├── README.md
│   │   │   ├── Start-Synapstor.ps1
│   │   │   ├── start-synapstor.bat
│   │   │   └── start-synapstor.sh
│   │   └── validators/
│   │       ├── __init__.py
│   │       ├── argument_validator.py # Validação de argumentos
│   │       └── config_validator.py   # Validação de config
│   └── web/                     # Interface web (futuro)
│       ├── __init__.py
│       ├── fastapi_app.py           # App FastAPI
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── knowledge_routes.py  # Rotas conhecimento
│       │   ├── memory_routes.py     # Rotas memória
│       │   └── embedding_routes.py  # Rotas embedding
│       └── middleware/
│           ├── __init__.py
│           └── web_middleware.py    # Middleware web
├── configuration/               # Configurações centralizadas
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base_settings.py         # Configurações base
│   │   ├── knowledge_settings.py    # Configurações conhecimento
│   │   ├── memory_settings.py       # Configurações memória
│   │   ├── embedding_settings.py    # Configurações embedding
│   │   ├── mcp_settings.py          # Configurações MCP
│   │   ├── storage_settings.py      # Configurações storage
│   │   ├── server_settings.py       # Configurações servidor
│   │   └── mef_settings.py          # Configurações MEF
│   ├── env_loader.py                # Carregador de ambiente
│   ├── config_builder.py            # Builder de configuração
│   └── validators/
│       ├── __init__.py
│       ├── settings_validator.py    # Validação de settings
│       └── env_validator.py         # Validação de env
└── shared/                      # Funcionalidades compartilhadas
    ├── __init__.py
    ├── common/
    │   ├── __init__.py
    │   ├── exceptions/
    │   │   ├── __init__.py
    │   │   ├── base_exception.py        # Exceção base
    │   │   ├── knowledge_exceptions.py  # Exceções conhecimento
    │   │   ├── memory_exceptions.py     # Exceções memória
    │   │   ├── embedding_exceptions.py  # Exceções embedding
    │   │   ├── mcp_exceptions.py        # Exceções MCP
    │   │   └── infrastructure_exceptions.py # Exceções infraestrutura
    │   ├── types/
    │   │   ├── __init__.py
    │   │   ├── common_types.py          # Tipos comuns
    │   │   ├── domain_types.py          # Tipos de domínio
    │   │   └── protocol_types.py        # Tipos de protocolo
    │   ├── interfaces/
    │   │   ├── __init__.py
    │   │   ├── repository_interface.py  # Interface repositório
    │   │   ├── service_interface.py     # Interface serviço
    │   │   └── provider_interface.py    # Interface provider
    │   └── constants/
    │       ├── __init__.py
    │       ├── mef_constants.py         # Constantes MEF
    │       ├── embedding_constants.py   # Constantes embedding
    │       └── protocol_constants.py    # Constantes protocolo
    ├── i18n/
    │   ├── __init__.py
    │   ├── translator.py                # Sistema de tradução
    │   ├── languages.py                 # Definição de idiomas
    │   ├── locale_detector.py           # Detector de locale
    │   ├── message_formatter.py         # Formatador de mensagens
    │   └── translations/
    │       ├── en.json                  # Traduções inglês
    │       ├── pt.json                  # Traduções português
    │       └── template.json            # Template traduções
    └── utils/
        ├── __init__.py
        ├── id_generator.py              # Gerador de IDs
        ├── file_utils.py                # Utilitários de arquivo
        ├── validation.py                # Validação geral
        ├── crypto_utils.py              # Utilitários cripto
        ├── date_utils.py                # Utilitários de data
        ├── string_utils.py              # Utilitários de string
        ├── collection_utils.py          # Utilitários de coleção
        └── performance_utils.py         # Utilitários de performance
```

## Detalhamento dos Domínios

### 1. Domínio Knowledge (Conhecimento)

**Responsabilidade**: Gerenciar todo o ciclo de vida do conhecimento, incluindo indexação, validação MEF, e busca semântica.

#### Entidades Principais
- **Document**: Representa um documento indexado no sistema
- **UKI (Unit of Knowledge Interlinked)**: Implementação da especificação MEF
- **KnowledgeUnit**: Unidade genérica de conhecimento
- **ContentMetadata**: Metadados associados ao conteúdo

#### Serviços Principais
- **IndexingService**: Coordena a indexação de documentos e UKIs
- **MEFService**: Implementa todas as funcionalidades específicas do MEF
- **SearchService**: Realiza buscas semânticas no conhecimento
- **ValidationService**: Valida estruturas de conhecimento e MEF

#### Value Objects
- **EmbeddingVector**: Representa um vetor de embedding
- **SearchCriteria**: Critérios e filtros para busca
- **DomainType**: Tipos de domínio suportados pelo MEF
- **KnowledgeContext**: Contexto em que o conhecimento é aplicado

### 2. Domínio Memory (Memória)

**Responsabilidade**: Gerenciar memórias conversacionais, contexto de sessões e estratégias de recuperação.

#### Entidades Principais
- **Memory**: Representa uma memória específica
- **Conversation**: Sessão de conversa com contexto
- **Context**: Contexto de uma conversa ou interação
- **Recall**: Processo de recuperação de memórias

#### Serviços Principais
- **MemoryService**: Gerencia criação, atualização e exclusão de memórias
- **RetrievalService**: Implementa estratégias de recuperação contextual
- **ContextService**: Gerencia contexto de conversas
- **ForgettingService**: Implementa estratégias de esquecimento

#### Value Objects
- **MemoryImportance**: Nível de importância de uma memória
- **RecallStrategy**: Estratégia para recuperação de memórias
- **TemporalContext**: Contexto temporal de memórias

### 3. Domínio Embedding

**Responsabilidade**: Gerenciar geração de embeddings, modelos e cálculos de similaridade.

#### Entidades Principais
- **Embedding**: Representa um embedding vetorial
- **Model**: Modelo de embedding utilizado
- **VectorSpace**: Espaço vetorial onde os embeddings residem
- **Similarity**: Cálculo e resultado de similaridade

#### Serviços Principais
- **EmbeddingService**: Gera embeddings para diferentes tipos de conteúdo
- **ModelService**: Gerencia modelos de embedding
- **SimilarityService**: Calcula similaridades entre embeddings
- **OptimizationService**: Otimiza embeddings para melhor performance

#### Providers
- **FastEmbedProvider**: Implementação usando FastEmbed
- **SentenceTransformerProvider**: Implementação usando Sentence Transformers
- **OpenAIProvider**: Implementação usando API da OpenAI

### 4. Domínio MCP (Model Context Protocol)

**Responsabilidade**: Implementar o protocolo MCP, gerenciar ferramentas e transportes.

#### Entidades Principais
- **Tool**: Representa uma ferramenta MCP
- **Transport**: Meio de comunicação (stdio, SSE, HTTP)
- **Session**: Sessão de comunicação MCP
- **Capability**: Capacidade do servidor MCP

#### Serviços Principais
- **ToolService**: Gerencia ferramentas disponíveis
- **TransportService**: Gerencia diferentes transportes
- **SessionService**: Gerencia sessões ativas
- **CapabilityService**: Gerencia capacidades do servidor

#### Ferramentas Específicas
- **MemoryTools**: Ferramentas para manipulação de memórias
- **SearchTools**: Ferramentas para busca semântica
- **BoilerplateTools**: Geração de código boilerplate
- **ChangelogTools**: Geração de changelogs
- **ModoSynapstor**: Sistema de raciocínio multidisciplinar

## Camadas Transversais

### Application Layer

**Responsabilidade**: Coordenar use cases que envolvem múltiplos domínios.

#### Orchestrators
- **ProjectIndexer**: Orquestra indexação completa de projetos
- **SemanticSearch**: Coordena busca entre conhecimento e memória
- **ModoSynapstor**: Implementa raciocínio multidisciplinar
- **KnowledgePipeline**: Pipeline completo de processamento

#### Use Cases
- **IndexProjectUseCase**: UC para indexar um projeto completo
- **SearchMemoryUseCase**: UC para buscar memórias específicas
- **StoreMemoryUseCase**: UC para armazenar novas memórias
- **ValidateMEFUseCase**: UC para validar estruturas MEF

### Infrastructure Layer

**Responsabilidade**: Implementar detalhes técnicos e integração com sistemas externos.

#### Persistence
- **Qdrant**: Integração com banco vetorial Qdrant
- **Local**: Armazenamento local para desenvolvimento
- **Adapters**: Adaptadores para diferentes domínios

#### External Services
- **FileProcessors**: Processamento de diferentes tipos de arquivo
- **APIs**: Integração com APIs externas (OpenAI, HuggingFace)

### Presentation Layer

**Responsabilidade**: Interfaces de usuário e protocolos de comunicação.

#### MCP Server
- **Server**: Servidor MCP principal
- **Handlers**: Manipuladores de diferentes tipos de requisição
- **Middleware**: Middlewares para autenticação, CORS, etc.

#### CLI
- **Commands**: Comandos da linha de comando
- **Controllers**: Controllers para coordenar ações
- **Validators**: Validação de entradas

### Configuration Layer

**Responsabilidade**: Centralizar todas as configurações do sistema.

#### Settings
- Configurações específicas por domínio
- Configurações de infraestrutura
- Configurações de apresentação

### Shared Layer

**Responsabilidade**: Funcionalidades compartilhadas entre todos os domínios.

#### Common
- **Exceptions**: Hierarquia de exceções
- **Types**: Tipos compartilhados
- **Interfaces**: Contratos compartilhados

#### I18n
- **Translator**: Sistema de tradução
- **Languages**: Definição de idiomas suportados

#### Utils
- Utilitários gerais para todo o sistema

## Padrões de Design Utilizados

### 1. Domain-Driven Design (DDD)
- **Bounded Contexts**: Cada domínio é um contexto limitado
- **Entities**: Objetos com identidade única
- **Value Objects**: Objetos imutáveis sem identidade
- **Services**: Lógica de negócio que não pertence a entidades
- **Repositories**: Abstração para persistência

### 2. Hexagonal Architecture
- **Ports**: Interfaces que definem contratos
- **Adapters**: Implementações específicas de infraestrutura
- **Core**: Lógica de negócio isolada

### 3. CQRS (Command Query Responsibility Segregation)
- **Commands**: Operações que modificam estado
- **Queries**: Operações de leitura
- **Handlers**: Manipuladores específicos

### 4. Event-Driven Architecture
- **Events**: Eventos de domínio
- **Handlers**: Manipuladores de eventos
- **Publishers**: Publicadores de eventos

### 5. Factory Pattern
- **EmbeddingProviderFactory**: Criação de providers
- **ToolFactory**: Criação de ferramentas
- **TransportFactory**: Criação de transportes

### 6. Strategy Pattern
- **RecallStrategy**: Estratégias de recuperação
- **ValidationStrategy**: Estratégias de validação
- **SerializationStrategy**: Estratégias de serialização

## Benefícios da Nova Arquitetura

### 1. Isolamento e Coesão
- Cada domínio tem responsabilidades bem definidas
- Mudanças em um domínio não afetam outros
- Alta coesão dentro de cada contexto

### 2. Escalabilidade
- Novos domínios podem ser adicionados facilmente
- Cada domínio pode ser desenvolvido independentemente
- Possibilidade de microserviços no futuro

### 3. Manutenibilidade
- Código mais organizado e fácil de entender
- Testes mais focados e isolados
- Facilita debugging e troubleshooting

### 4. Testabilidade
- Testes unitários por domínio
- Mocks e stubs mais simples
- Testes de integração bem definidos

### 5. Especialização de Equipes
- Diferentes desenvolvedores podem focar em domínios específicos
- Conhecimento especializado por área
- Desenvolvimento paralelo mais eficiente

### 6. Alinhamento com MEF
- Estrutura natural para Matrix Embedding Framework
- Separação clara entre tipos de conhecimento
- Facilita evolução das especificações MEF

## Impacto nas Funcionalidades Existentes

### MEF (Matrix Embedding Framework)
- Domínio Knowledge concentra toda lógica MEF
- MEFService centraliza validação e processamento
- UKI como entidade principal do domínio

### Modo Synapstor
- Fica no domínio MCP como ferramenta especializada
- Utiliza serviços de Knowledge e Memory
- Mantém integração com RAG dinâmico

### Sistema de Plugins
- Ferramentas MCP organizadas por categoria
- Cada ferramenta em seu domínio apropriado
- Factory pattern para criação dinâmica

### Internacionalização
- Sistema compartilhado entre todos os domínios
- Configuração centralizada
- Traduções organizadas por contexto

## Considerações de Implementação

### 1. Migração Gradual
- Implementar um domínio por vez
- Manter compatibilidade durante transição
- Testes de regressão contínuos

### 2. Dependency Injection
- Utilizar DI container para gerenciar dependências
- Facilitar testes com mocks
- Configuração flexível de implementações

### 3. Event Sourcing (Futuro)
- Preparar arquitetura para Event Sourcing
- Versionamento de eventos
- Replay de eventos para debugging

### 4. Monitoring e Observabilidade
- Logs estruturados por domínio
- Métricas específicas de cada contexto
- Tracing distribuído para debugging

### 5. Documentação
- Documentação por domínio
- Exemplos de uso específicos
- Guias de desenvolvimento

## Próximos Passos

### Fase 1: Preparação
1. Criar estrutura de diretórios
2. Definir interfaces principais
3. Configurar sistema de DI

### Fase 2: Domínio Embedding
1. Migrar providers existentes
2. Implementar novos serviços
3. Criar testes unitários

### Fase 3: Domínio Knowledge
1. Migrar lógica de indexação
2. Implementar MEF Service
3. Criar repositórios

### Phase 4: Memory Domain
1. Extrair lógica de memória
2. Implementar estratégias de recuperação
3. Criar serviços de contexto

### Fase 5: Domínio MCP
1. Migrar ferramentas existentes
2. Implementar novos transportes
3. Criar sistema de capacidades

### Fase 6: Integration
1. Conectar todos os domínios
2. Implementar orchestrators
3. Testes de integração completos

### Fase 7: CLI e Presentation
1. Migrar comandos CLI
2. Implementar novos controllers
3. Criar interfaces web (futuro)

Esta arquitetura representa uma evolução significativa do Synapstor, proporcionando uma base sólida para crescimento futuro e manutenção eficiente do código.

---

# EXECUTION, VALIDATION AND APPROVAL STRUCTURE

## Implementation Methodology

### Fundamental Principles
1. **Test-Driven Development (TDD)**: Tests written before code
2. **Behavior-Driven Development (BDD)**: Specifications in natural language
3. **Quality Gates**: Mandatory quality gates between phases
4. **Continuous Integration**: Continuous integration with automatic validation
5. **Definition of Done**: Clear completion criteria
6. **Internationalization First**: All code, tests, and documentation must support i18n from the start

## Internationalization (i18n) Architecture Considerations

### Core Requirements
- **All user-facing text MUST use the i18n system**
- **All error messages MUST be translatable**
- **All BDD scenarios MUST be in English (primary language)**
- **All code comments and documentation MUST be in English**
- **All variable names and function names MUST be in English**
- **Translation keys MUST follow consistent naming conventions**

### i18n System Integration Points
```
┌─────────────────────────────────────────────────────────────┐
│                    i18n System Architecture                 │
├─────────────────────────────────────────────────────────────┤
│ Domains:                                                    │
│ ├── knowledge/    → MEF validation messages                 │
│ ├── memory/       → Memory management messages              │
│ ├── embedding/    → Provider error messages                 │
│ └── mcp/          → Tool descriptions and responses         │
│                                                             │
│ Application:                                                │
│ ├── use_cases/    → Business logic error messages          │
│ └── dto/          → Validation error messages               │
│                                                             │
│ Presentation:                                               │
│ ├── cli/          → Command help and error messages        │
│ └── mcp_server/   → Tool descriptions and responses        │
│                                                             │
│ Shared:                                                     │
│ └── i18n/         → Translation engine and messages        │
└─────────────────────────────────────────────────────────────┘
```

### Translation Key Conventions
```
Format: {domain}.{component}.{type}.{specific_key}

Examples:
- knowledge.mef.validation.missing_required_field
- embedding.service.error.provider_initialization_failed
- mcp.tools.memory.description
- cli.indexer.help.project_argument
- application.search.error.invalid_filters
```

### Quality Structure

#### Test Pyramid
```
                    E2E Tests (Few)
                   /                \
              Integration Tests      \
             /                      \
        Unit Tests (Many)           \
       /                            \
   BDD Specs                    Contract Tests
```

## DETAILED IMPLEMENTATION PHASES

### Phase 1: Preparation and Base Infrastructure

#### 1.1 Specific Objectives
- [ ] Create complete directory structure
- [ ] Implement Dependency Injection system
- [ ] Configure test pipeline
- [ ] Establish code standards
- [ ] Configure i18n system integration
- [ ] Validate translation key consistency

#### 1.2 BDD Acceptance Criteria

**Feature: Directory Structure**
```gherkin
Feature: New architecture directory structure
  As a developer
  I want a well-organized directory structure
  So that I can easily navigate and maintain the code

  Background:
    Given I am at the Synapstor project root
    And the new architecture structure has been created

  Scenario: Verify domain structure
    When I navigate to src/synapstor/domains directory
    Then I should see the directories:
      | directory  |
      | knowledge  |
      | memory     |
      | embedding  |
      | mcp        |
    And each directory should contain the subdirectories:
      | subdirectory    |
      | entities        |
      | services        |
      | repositories    |
      | value_objects   |

  Scenario: Verify layer structure
    When I navigate to src/synapstor directory
    Then I should see the layer directories:
      | layer          |
      | domains        |
      | application    |
      | infrastructure |
      | presentation   |
      | configuration  |
      | shared         |

  Scenario: Verify __init__.py files
    When I check all Python directories
    Then each directory should contain an __init__.py file
    And each __init__.py should have adequate documentation in English
```

**Feature: Internationalization System Integration**
```gherkin
Feature: i18n system integration in new architecture
  As a developer
  I want all components to properly use the i18n system
  So that the application can support multiple languages

  Background:
    Given the i18n system is configured
    And translation files exist for supported languages
    And all components use the translator instance

  Scenario: Validate translation key consistency
    When I scan all source code files
    Then all hardcoded user-facing strings should use translation keys
    And all translation keys should follow the naming convention
    And no English text should be hardcoded in business logic
    And all error messages should use the translator

  Scenario: Verify domain-specific translations
    Given a domain service that generates user messages
    When the service creates an error message
    Then it should use a translation key from its domain namespace
    And the message should be properly translated to the current language
    And the translation key should follow the format: {domain}.{component}.{type}.{key}

  Scenario: CLI commands internationalization
    Given CLI commands are available
    When I request help for any command
    Then all help text should be translated
    And command descriptions should use translation keys
    And error messages should be properly internationalized
```

**Feature: Dependency Injection System**
```gherkin
Feature: Dependency injection system
  As a developer
  I want a configured DI system
  So that I can manage dependencies between components

  Scenario: Configure DI container
    Given I have defined interfaces
    When I configure the DI container
    Then all dependencies should be resolved automatically
    And there should be no circular dependencies
    And all implementations should be registered

  Scenario: Test dependency resolution
    Given a service that depends on a repository
    When I request the service from the container
    Then the repository should be injected automatically
    And the instance should be functional
```

#### 1.3 Validation Data

**Directory Structure - Complete Checklist**
```yaml
validation_data:
  directory_structure:
    - path: "src/synapstor/domains/knowledge"
      required_files: ["__init__.py"]
      required_dirs: ["entities", "services", "repositories", "value_objects", "specifications"]
    - path: "src/synapstor/domains/memory"
      required_files: ["__init__.py"]
      required_dirs: ["entities", "services", "repositories", "value_objects"]
    - path: "src/synapstor/domains/embedding"
      required_files: ["__init__.py"]
      required_dirs: ["entities", "services", "providers", "value_objects", "repositories"]
    - path: "src/synapstor/domains/mcp"
      required_files: ["__init__.py"]
      required_dirs: ["entities", "services", "tools", "transports", "value_objects"]
    - path: "src/synapstor/application"
      required_files: ["__init__.py"]
      required_dirs: ["orchestrators", "use_cases", "dto", "events", "workflows"]
    - path: "src/synapstor/infrastructure"
      required_files: ["__init__.py"]
      required_dirs: ["persistence", "messaging", "serialization", "monitoring", "external"]
    - path: "src/synapstor/presentation"
      required_files: ["__init__.py"]
      required_dirs: ["mcp_server", "cli", "web"]
    - path: "src/synapstor/configuration"
      required_files: ["__init__.py", "env_loader.py", "config_builder.py"]
      required_dirs: ["settings", "validators"]
    - path: "src/synapstor/shared"
      required_files: ["__init__.py"]
      required_dirs: ["common", "i18n", "utils"]

  dependency_injection:
    container_type: "python-dependency-injector"
    required_bindings:
      - interface: "EmbeddingProviderInterface"
        implementations: ["FastEmbedProvider", "SentenceTransformerProvider"]
      - interface: "KnowledgeRepositoryInterface"
        implementations: ["QdrantKnowledgeRepository"]
      - interface: "MemoryRepositoryInterface"
        implementations: ["QdrantMemoryRepository"]

  i18n_validation:
    required_translation_files:
      - "src/synapstor/shared/i18n/translations/en.json"
      - "src/synapstor/shared/i18n/translations/pt.json"
    
    translation_key_patterns:
      - "knowledge\\..*"          # knowledge domain keys
      - "memory\\..*"             # memory domain keys  
      - "embedding\\..*"          # embedding domain keys
      - "mcp\\..*"                # mcp domain keys
      - "application\\..*"        # application layer keys
      - "cli\\..*"                # cli presentation keys
      - "common\\..*"             # shared common keys
    
    forbidden_patterns:
      - hardcoded_strings: ["Error:", "Success:", "Warning:", "Info:"]
      - non_english_comments: true
      - non_english_variables: true
      - direct_print_statements: true
    
    required_translator_usage:
      - all_exception_messages: true
      - all_cli_output: true
      - all_tool_descriptions: true
      - all_validation_messages: true
```

#### 1.4 Validation Tests

**test_phase1_structure.py**
```python
import pytest
import os
import re
import json
from pathlib import Path
from synapstor.shared.i18n import get_translator

class TestPhase1Structure:
    """Tests to validate Phase 1 structure and internationalization"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent
    
    @pytest.fixture
    def synapstor_src(self, project_root):
        return project_root / "src" / "synapstor"
    
    @pytest.fixture
    def translator(self):
        return get_translator()
    
    def test_domain_directories_exist(self, synapstor_src):
        """Test if all domain directories exist"""
        expected_domains = ["knowledge", "memory", "embedding", "mcp"]
        domains_path = synapstor_src / "domains"
        
        assert domains_path.exists(), "Domains directory does not exist"
        
        for domain in expected_domains:
            domain_path = domains_path / domain
            assert domain_path.exists(), f"Domain {domain} does not exist"
            assert (domain_path / "__init__.py").exists(), f"__init__.py does not exist in {domain}"
    
    def test_layer_directories_exist(self, synapstor_src):
        """Test if all layer directories exist"""
        expected_layers = [
            "domains", "application", "infrastructure", 
            "presentation", "configuration", "shared"
        ]
        
        for layer in expected_layers:
            layer_path = synapstor_src / layer
            assert layer_path.exists(), f"Layer {layer} does not exist"
            assert (layer_path / "__init__.py").exists(), f"__init__.py does not exist in {layer}"
    
    def test_domain_subdirectories(self, synapstor_src):
        """Test if each domain has the necessary subdirectories"""
        domains = ["knowledge", "memory", "embedding", "mcp"]
        required_subdirs = ["entities", "services", "repositories", "value_objects"]
        
        for domain in domains:
            domain_path = synapstor_src / "domains" / domain
            for subdir in required_subdirs:
                subdir_path = domain_path / subdir
                assert subdir_path.exists(), f"Subdirectory {subdir} does not exist in {domain}"
                assert (subdir_path / "__init__.py").exists(), f"__init__.py does not exist in {domain}/{subdir}"
    
    def test_i18n_system_integration(self, synapstor_src, translator):
        """Test if i18n system is properly integrated"""
        # Check translation files exist
        i18n_path = synapstor_src / "shared" / "i18n" / "translations"
        assert i18n_path.exists(), "i18n translations directory does not exist"
        
        en_file = i18n_path / "en.json"
        pt_file = i18n_path / "pt.json"
        assert en_file.exists(), "English translation file does not exist"
        assert pt_file.exists(), "Portuguese translation file does not exist"
        
        # Validate JSON structure
        with open(en_file) as f:
            en_translations = json.load(f)
        with open(pt_file) as f:
            pt_translations = json.load(f)
        
        assert isinstance(en_translations, dict), "English translations should be a dictionary"
        assert isinstance(pt_translations, dict), "Portuguese translations should be a dictionary"
        
        # Check translator is working
        test_message = translator.translate("common.test.message", default="Test message")
        assert test_message is not None, "Translator should return a message"
    
    def test_no_hardcoded_strings_in_business_logic(self, synapstor_src):
        """Test that business logic does not contain hardcoded user-facing strings"""
        forbidden_patterns = [
            r'print\s*\(\s*["\'](?!DEBUG|INFO|WARNING|ERROR)[^"\']*["\']',  # Direct print with strings
            r'raise\s+\w+Exception\s*\(\s*["\'][^"\']*["\']',  # Exception with hardcoded message
            r'logging\.\w+\s*\(\s*["\'][^"\']*["\']',  # Logging with hardcoded message
        ]
        
        python_files = list(synapstor_src.rglob("*.py"))
        violations = []
        
        for file_path in python_files:
            # Skip test files and migration files
            if "test" in str(file_path) or "migration" in str(file_path):
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in forbidden_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    violations.append(f"{file_path}: {matches}")
        
        assert not violations, f"Found hardcoded strings in business logic: {violations}"
    
    def test_translation_key_consistency(self, synapstor_src):
        """Test that all translation keys follow the naming convention"""
        translation_pattern = r'translator\.translate\s*\(\s*["\']([^"\']+)["\']'
        python_files = list(synapstor_src.rglob("*.py"))
        
        invalid_keys = []
        valid_prefixes = ["knowledge.", "memory.", "embedding.", "mcp.", "application.", "cli.", "common."]
        
        for file_path in python_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            matches = re.findall(translation_pattern, content)
            for key in matches:
                if not any(key.startswith(prefix) for prefix in valid_prefixes):
                    invalid_keys.append(f"{file_path}: {key}")
        
        assert not invalid_keys, f"Found invalid translation keys: {invalid_keys}"
```

### Phase 2: Embedding Domain

#### 2.1 Specific Objectives
- [ ] Migrate existing providers to new structure
- [ ] Implement EmbeddingService with clear interface
- [ ] Create embedding cache system
- [ ] Implement quality metrics
- [ ] Ensure all error messages use i18n system
- [ ] Validate translation keys for embedding domain

#### 2.2 BDD Acceptance Criteria

**Feature: EmbeddingService**
```gherkin
Feature: Embedding generation service
  As a knowledge system
  I want to generate high-quality embeddings
  So that I can enable precise semantic search

  Background:
    Given the EmbeddingService is configured
    And the FastEmbed provider is available
    And the model "sentence-transformers/all-MiniLM-L6-v2" is loaded
    And all error messages use the translator with "embedding." prefix

  Scenario: Generate embedding for simple text
    Given a text "This is an example sentence for embedding"
    When I request embedding generation
    Then I should receive a 384-dimensional vector
    And the vector should not contain NaN or infinite values
    And the processing time should be less than 1 second
    And any error messages should use translation keys like "embedding.service.error.*"

  Scenario: Generate embeddings in batch
    Given a list of 100 different texts
    When I request batch embedding generation
    Then I should receive 100 vectors
    And all vectors should have the same dimension
    And the total time should be less than 5 seconds
    And it should use parallelization when possible
    And any error messages should be properly internationalized

  Scenario: Embedding cache functionality
    Given a text "Text to test cache functionality"
    And I have already generated an embedding for this text previously
    When I request the embedding again
    Then the result should come from cache
    And the response time should be less than 0.1 seconds
    And the vector should be identical to the previous one
    And cache hit/miss messages should use translation keys

  Scenario: Embedding provider switching
    Given I am using FastEmbed provider
    When I configure the system to use SentenceTransformer
    Then the service should switch providers automatically
    And embeddings should use the new model
    And there should be no configuration errors
    And all status messages should be properly translated

  Scenario: Error handling with internationalization
    Given an invalid model name is configured
    When I try to generate an embedding
    Then an appropriate exception should be raised
    And the error message should use "embedding.provider.error.invalid_model" translation key
    And the message should be displayed in the current language
```

**Feature: Similarity Service**
```gherkin
Feature: Similarity calculation between embeddings
  As a search system
  I want to calculate precise similarities
  So that I can return relevant results

  Background:
    Given the SimilarityService is configured
    And all messages use the translator with "embedding.similarity." prefix

  Scenario: Calculate cosine similarity
    Given two known test embeddings
    When I calculate the cosine similarity
    Then the result should be between 0 and 1
    And it should be reproducible across multiple executions
    And any error messages should use "embedding.similarity.error.*" keys

  Scenario: Batch similarity search
    Given a query embedding
    And a collection of 1000 embeddings
    When I search for the 10 most similar ones
    Then I should receive exactly 10 results
    And the results should be ordered by similarity
    And the first result should have the highest similarity
    And progress messages should be properly internationalized
```

#### 2.3 Translation Usage Examples

**Example: Embedding Service with i18n**
```python
from synapstor.shared.i18n import get_translator
from synapstor.domains.embedding.services.embedding_service import EmbeddingService

class EmbeddingService:
    def __init__(self):
        self.translator = get_translator()
    
    def generate_embedding(self, text: str) -> List[float]:
        try:
            # Business logic here
            embedding = self._provider.encode(text)
            
            # Success message using translation
            self.logger.info(
                self.translator.translate(
                    "embedding.service.success.generated",
                    text_length=len(text),
                    vector_size=len(embedding)
                )
            )
            return embedding
            
        except Exception as e:
            # Error message using translation
            error_msg = self.translator.translate(
                "embedding.service.error.generation_failed",
                error=str(e)
            )
            raise EmbeddingGenerationError(error_msg)
    
    def validate_model(self, model_name: str) -> bool:
        if not model_name:
            raise ValueError(
                self.translator.translate("embedding.provider.error.empty_model_name")
            )
        
        if not self._is_model_supported(model_name):
            raise ValueError(
                self.translator.translate(
                    "embedding.provider.error.unsupported_model",
                    model=model_name
                )
            )
        return True
```

**Translation Files Structure**
```json
// en.json
{
  "embedding": {
    "service": {
      "success": {
        "generated": "Successfully generated embedding for text of {text_length} characters (vector size: {vector_size})"
      },
      "error": {
        "generation_failed": "Failed to generate embedding: {error}",
        "invalid_input": "Invalid input text provided"
      }
    },
    "provider": {
      "error": {
        "empty_model_name": "Model name cannot be empty",
        "unsupported_model": "Model '{model}' is not supported",
        "initialization_failed": "Failed to initialize embedding provider: {error}"
      }
    },
    "similarity": {
      "error": {
        "dimension_mismatch": "Vector dimensions do not match: {dim1} vs {dim2}",
        "invalid_vectors": "Invalid vector data provided"
      }
    }
  }
}

// pt.json
{
  "embedding": {
    "service": {
      "success": {
        "generated": "Embedding gerado com sucesso para texto de {text_length} caracteres (tamanho do vetor: {vector_size})"
      },
      "error": {
        "generation_failed": "Falha ao gerar embedding: {error}",
        "invalid_input": "Texto de entrada inválido fornecido"
      }
    },
    "provider": {
      "error": {
        "empty_model_name": "Nome do modelo não pode estar vazio",
        "unsupported_model": "Modelo '{model}' não é suportado",
        "initialization_failed": "Falha ao inicializar provedor de embedding: {error}"
      }
    },
    "similarity": {
      "error": {
        "dimension_mismatch": "Dimensões dos vetores não coincidem: {dim1} vs {dim2}",
        "invalid_vectors": "Dados de vetor inválidos fornecidos"
      }
    }
  }
}
```

#### 2.4 Validation Data

**embedding_test_data.yaml**
```yaml
test_data:
  sample_texts:
    - text: "This is an example sentence for embedding"
      expected_dimensions: 384
      language: "en"
    - text: "Machine learning and artificial intelligence"
      expected_dimensions: 384
      language: "en"
    - text: "Natural language processing with transformers"
      expected_dimensions: 384
      language: "en"
  
  performance_benchmarks:
    single_embedding:
      max_time_seconds: 1.0
      max_memory_mb: 100
    batch_embedding:
      batch_size: 100
      max_time_seconds: 5.0
      max_memory_mb: 500
  
  similarity_test_cases:
    - text1: "cat animal feline"
      text2: "feline domestic animal"
      expected_similarity_min: 0.7
    - text1: "Python programming code"
      text2: "software development application"
      expected_similarity_min: 0.5
    - text1: "cat animal"
      text2: "car automobile"
      expected_similarity_max: 0.3

  providers_config:
    fastembed:
      model: "sentence-transformers/all-MiniLM-L6-v2"
      dimensions: 384
      supported_languages: ["en", "pt"]
    sentence_transformers:
      model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
      dimensions: 384
      supported_languages: ["en", "pt", "es", "fr"]

  i18n_test_data:
    translation_keys_to_validate:
      - "embedding.service.success.generated"
      - "embedding.service.error.generation_failed"
      - "embedding.provider.error.empty_model_name"
      - "embedding.provider.error.unsupported_model"
      - "embedding.similarity.error.dimension_mismatch"
    
    error_scenarios:
      - scenario: "invalid_model_name"
        expected_key: "embedding.provider.error.unsupported_model"
        variables: ["model"]
      - scenario: "empty_input_text"
        expected_key: "embedding.service.error.invalid_input"
        variables: []
      - scenario: "dimension_mismatch"
        expected_key: "embedding.similarity.error.dimension_mismatch"
        variables: ["dim1", "dim2"]
```

#### 2.5 Implementation Tests with i18n Validation

**test_embedding_domain.py**
```python
import pytest
import numpy as np
import json
from unittest.mock import Mock, patch
from synapstor.domains.embedding.services.embedding_service import EmbeddingService
from synapstor.domains.embedding.services.similarity_service import SimilarityService
from synapstor.domains.embedding.providers.fastembed_provider import FastEmbedProvider
from synapstor.shared.i18n import get_translator, set_language, SupportedLanguages

class TestEmbeddingDomain:
    """Complete tests for Embedding domain with i18n validation"""
    
    @pytest.fixture
    def embedding_service(self):
        provider = Mock(spec=FastEmbedProvider)
        return EmbeddingService(provider=provider)
    
    @pytest.fixture
    def similarity_service(self):
        return SimilarityService()
    
    @pytest.fixture
    def translator(self):
        return get_translator()
    
    def test_embedding_generation_performance(self, embedding_service):
        """Test embedding generation performance"""
        import time
        
        text = "This is an example sentence for embedding"
        
        start_time = time.time()
        embedding = embedding_service.generate_embedding(text)
        end_time = time.time()
        
        # Performance validations
        assert (end_time - start_time) < 1.0, "Embedding should be generated in less than 1 second"
        assert len(embedding) == 384, "Embedding should have 384 dimensions"
        assert not np.isnan(embedding).any(), "Embedding should not contain NaN values"
        assert not np.isinf(embedding).any(), "Embedding should not contain infinite values"
    
    def test_batch_embedding_efficiency(self, embedding_service):
        """Test batch embedding efficiency"""
        texts = [f"Example text number {i}" for i in range(100)]
        
        import time
        start_time = time.time()
        embeddings = embedding_service.generate_batch_embeddings(texts)
        end_time = time.time()
        
        assert len(embeddings) == 100, "Should generate 100 embeddings"
        assert (end_time - start_time) < 5.0, "Batch should be processed in less than 5 seconds"
        assert all(len(emb) == 384 for emb in embeddings), "All embeddings should have 384 dimensions"
    
    def test_similarity_calculation_accuracy(self, similarity_service):
        """Test accuracy of similarity calculation"""
        # Known test vectors
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])  # Identical
        vec3 = np.array([0.0, 1.0, 0.0])  # Orthogonal
        
        # Test identical similarity
        sim_identical = similarity_service.cosine_similarity(vec1, vec2)
        assert abs(sim_identical - 1.0) < 1e-6, "Identical vectors should have similarity 1.0"
        
        # Test orthogonal similarity
        sim_orthogonal = similarity_service.cosine_similarity(vec1, vec3)
        assert abs(sim_orthogonal - 0.0) < 1e-6, "Orthogonal vectors should have similarity 0.0"
    
    def test_embedding_cache_functionality(self, embedding_service):
        """Test cache functionality"""
        text = "Text to test cache functionality"
        
        # First generation
        import time
        start_time = time.time()
        embedding1 = embedding_service.generate_embedding(text)
        first_time = time.time() - start_time
        
        # Second generation (should use cache)
        start_time = time.time()
        embedding2 = embedding_service.generate_embedding(text)
        second_time = time.time() - start_time
        
        assert np.array_equal(embedding1, embedding2), "Cache embeddings should be identical"
        assert second_time < 0.1, "Cache should return in less than 0.1 seconds"
        assert second_time < first_time, "Cache should be faster than generation"
    
    def test_i18n_error_messages(self, embedding_service, translator):
        """Test that error messages use proper translation keys"""
        # Test invalid model error
        with pytest.raises(ValueError) as exc_info:
            embedding_service.validate_model("")
        
        error_message = str(exc_info.value)
        # Verify the error message was translated
        expected_key = "embedding.provider.error.empty_model_name"
        expected_message = translator.translate(expected_key)
        assert error_message == expected_message, f"Error message should use translation key {expected_key}"
    
    def test_i18n_translation_key_coverage(self, translator):
        """Test that all required translation keys exist"""
        required_keys = [
            "embedding.service.success.generated",
            "embedding.service.error.generation_failed",
            "embedding.provider.error.empty_model_name",
            "embedding.provider.error.unsupported_model",
            "embedding.similarity.error.dimension_mismatch"
        ]
        
        for key in required_keys:
            # Test English
            set_language(SupportedLanguages.ENGLISH)
            en_message = translator.translate(key)
            assert en_message != key, f"English translation missing for key: {key}"
            
            # Test Portuguese
            set_language(SupportedLanguages.PORTUGUESE)
            pt_message = translator.translate(key)
            assert pt_message != key, f"Portuguese translation missing for key: {key}"
            assert pt_message != en_message, f"Portuguese translation should differ from English for key: {key}"
    
    def test_i18n_variable_interpolation(self, translator):
        """Test that translation variable interpolation works correctly"""
        set_language(SupportedLanguages.ENGLISH)
        
        # Test with variables
        message = translator.translate(
            "embedding.service.success.generated",
            text_length=100,
            vector_size=384
        )
        
        assert "100" in message, "Text length variable should be interpolated"
        assert "384" in message, "Vector size variable should be interpolated"
        
        # Test Portuguese
        set_language(SupportedLanguages.PORTUGUESE)
        pt_message = translator.translate(
            "embedding.service.success.generated",
            text_length=100,
            vector_size=384
        )
        
        assert "100" in pt_message, "Text length variable should be interpolated in Portuguese"
        assert "384" in pt_message, "Vector size variable should be interpolated in Portuguese"
    
    def test_no_hardcoded_strings_in_service(self):
        """Test that the embedding service doesn't contain hardcoded user-facing strings"""
        import inspect
        
        # Get the source code of EmbeddingService
        source = inspect.getsource(EmbeddingService)
        
        # Check for common hardcoded patterns
        forbidden_patterns = [
            "print(",
            "Error:",
            "Warning:",
            "Success:",
            "Failed to",
            "Cannot"
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"Found potential hardcoded string pattern: {pattern}"
```

### Phase 3: Knowledge Domain

#### 3.1 Specific Objectives
- [ ] Implement Document and UKI entities  
- [ ] Create IndexingService with complete MEF support
- [ ] Implement SearchService with advanced filters
- [ ] Create ValidationService for MEF structures
- [ ] Ensure all MEF validation messages use i18n system
- [ ] Validate translation keys for knowledge domain

#### 3.2 BDD Acceptance Criteria

**Feature: MEF Document Processing**
```gherkin
Feature: MEF document processing
  As a knowledge system
  I want to process documents in MEF format
  So that I can structure knowledge in a standardized way

  Background:
    Given the MEFService is configured
    And MEF validations are active
    And all validation messages use the translator with "knowledge.mef." prefix

  Scenario: Process valid UKI
    Given a YAML file with valid MEF structure:
      """
      id: unik-test-example
      title: Test Example
      domain: technical
      type: pattern
      context: implementation
      content: |
        This is an example UKI for testing purposes
      examples:
        - input: "example input"
          output: "example output"
      intent_of_use:
        - validate_implementation
      use_case_stage:
        - implementation
      related_to:
        - unik-other-example
      """
    When I process the document
    Then the UKI should be created successfully
    And all required fields should be present
    And the metadata should be correct
    And the embedding should be generated
    And success messages should use "knowledge.mef.success.*" translation keys

  Scenario: Reject invalid UKI
    Given a YAML file with invalid MEF structure:
      """
      title: Invalid Example
      content: Content without ID
      """
    When I process the document
    Then a validation exception should be raised
    And the message should use "knowledge.mef.validation.missing_required_field" translation key
    And the document should not be indexed
    And the error should be properly internationalized

  Scenario: Process non-MEF document
    Given a common text file:
      """
      This is a common text document
      without MEF structure.
      """
    When I process the document
    Then a common Document should be created
    And the embedding should be generated
    And there should be no MEF validation
    And processing messages should use "knowledge.document.*" translation keys
```

**Feature: Advanced Search with MEF Filters**
```gherkin
Feature: Advanced search with MEF filters
  As a system user
  I want to search knowledge with specific filters
  So that I can find relevant information quickly

  Background:
    Given a knowledge base exists with:
      | id               | domain    | type     | context        |
      | unik-auth-jwt    | technical | pattern  | implementation |
      | unik-auth-oauth  | technical | pattern  | implementation |
      | unik-discount    | business  | rule     | validation     |
      | unik-ui-modal    | product   | guideline| design         |
    And all search messages use the translator with "knowledge.search." prefix

  Scenario: Search by specific domain
    When I search for "authentication" with filter domain="technical"
    Then I should receive only results from technical domain
    And the results should include "unik-auth-jwt" and "unik-auth-oauth"
    And it should not include results from other domains
    And search result messages should use "knowledge.search.success.*" translation keys

  Scenario: Search by type and context
    When I search for "pattern" with filters type="pattern" and context="implementation"
    Then I should receive only implementation patterns
    And the results should be ordered by relevance
    And each result should include MEF metadata
    And filter messages should be properly internationalized

  Scenario: Semantic search with combined filters
    Given a query "how to validate discount"
    When I search with filters domain="business" and type="rule"
    Then the result should include "unik-discount"
    And it should have high semantic similarity
    And it should respect all applied filters
    And search progress messages should use translation keys
```

#### 3.3 Validation Data

**knowledge_test_data.yaml**
```yaml
test_data:
  valid_mef_documents:
    - id: "unik-test-auth-pattern"
      title: "JWT Authentication Pattern"
      domain: "technical"
      type: "pattern"
      context: "implementation"
      content: |
        Pattern for implementing JWT authentication in web applications.
        Includes token generation, validation, and refresh mechanisms.
      examples:
        - input: "User login with valid credentials"
          output: "JWT token with 15min expiration"
        - input: "Request with expired token"
          output: "401 Unauthorized with refresh instruction"
      intent_of_use:
        - "validate_implementation"
        - "generate_authentication_code"
      use_case_stage:
        - "implementation"
        - "peer_review"
      related_to:
        - "unik-test-oauth-pattern"
        - "unik-test-security-headers"

  invalid_mef_documents:
    - error_type: "missing_required_field"
      document:
        title: "Document without ID"
        content: "This document is missing required ID field"
      expected_error: "Field 'id' is required"
    
    - error_type: "invalid_domain"
      document:
        id: "unik-invalid-domain"
        title: "Invalid Domain Test"
        domain: "invalid_domain_value"
        type: "pattern"
        context: "implementation"
        content: "Test content"
      expected_error: "Domain 'invalid_domain_value' is not supported"

  search_test_cases:
    - query: "authentication JWT token"
      filters:
        domain: "technical"
        type: "pattern"
      expected_results:
        - "unik-test-auth-pattern"
      min_similarity: 0.8
    
    - query: "business rule validation"
      filters:
        domain: "business"
        type: "rule"
      expected_results:
        - "unik-discount-rule"
      min_similarity: 0.7

  performance_benchmarks:
    indexing:
      documents_per_second: 50
      max_memory_per_document_mb: 10
    searching:
      max_response_time_ms: 500
      concurrent_searches: 10
```

#### 3.4 Implementation Tests

**test_knowledge_domain.py**
```python
import pytest
from synapstor.domains.knowledge.entities.uki import UKI
from synapstor.domains.knowledge.entities.document import Document
from synapstor.domains.knowledge.services.mef_service import MEFService
from synapstor.domains.knowledge.services.search_service import SearchService

class TestKnowledgeDomain:
    """Complete tests for Knowledge domain"""
    
    @pytest.fixture
    def mef_service(self):
        return MEFService()
    
    @pytest.fixture
    def search_service(self):
        return SearchService()
    
    def test_valid_mef_document_creation(self, mef_service):
        """Test creation of valid MEF document"""
        mef_data = {
            "id": "unik-test-example",
            "title": "Test Example",
            "domain": "technical",
            "type": "pattern",
            "context": "implementation",
            "content": "Test content for UKI",
            "examples": [{"input": "test", "output": "result"}],
            "intent_of_use": ["validate_implementation"],
            "use_case_stage": ["implementation"],
            "related_to": ["unik-other-example"]
        }
        
        uki = mef_service.create_uki(mef_data)
        
        assert isinstance(uki, UKI)
        assert uki.id == "unik-test-example"
        assert uki.domain == "technical"
        assert uki.type == "pattern"
        assert len(uki.examples) == 1
        assert "validate_implementation" in uki.intent_of_use
    
    def test_invalid_mef_document_rejection(self, mef_service):
        """Test rejection of invalid MEF document"""
        invalid_data = {
            "title": "Missing ID",
            "content": "Content without required ID"
        }
        
        with pytest.raises(ValueError) as exc_info:
            mef_service.create_uki(invalid_data)
        
        assert "Field 'id' is required" in str(exc_info.value)
    
    def test_search_with_mef_filters(self, search_service):
        """Test search with MEF filters"""
        # Setup: add test documents to index
        test_documents = [
            UKI(
                id="unik-auth-jwt",
                title="JWT Authentication",
                domain="technical",
                type="pattern",
                context="implementation",
                content="JWT authentication pattern",
                embedding=[0.1] * 384
            ),
            UKI(
                id="unik-discount-rule",
                title="Discount Business Rule",
                domain="business",
                type="rule",
                context="validation",
                content="Business rule for discount validation",
                embedding=[0.2] * 384
            )
        ]
        
        for doc in test_documents:
            search_service.index_document(doc)
        
        # Test search with domain filter
        results = search_service.search(
            query="authentication",
            filters={"domain": "technical"}
        )
        
        assert len(results) == 1
        assert results[0].id == "unik-auth-jwt"
        assert results[0].domain == "technical"
    
    def test_indexing_performance(self, mef_service):
        """Test indexing performance"""
        documents = []
        for i in range(100):
            doc_data = {
                "id": f"unik-perf-test-{i}",
                "title": f"Performance Test {i}",
                "domain": "technical",
                "type": "pattern",
                "context": "implementation",
                "content": f"Performance test content {i}"
            }
            documents.append(doc_data)
        
        import time
        start_time = time.time()
        
        for doc_data in documents:
            mef_service.create_uki(doc_data)
        
        end_time = time.time()
        total_time = end_time - start_time
        docs_per_second = len(documents) / total_time
        
        assert docs_per_second >= 50, f"Expected at least 50 docs/sec, got {docs_per_second}"
```

### Phase 4: Memory Domain

#### 4.1 BDD Acceptance Criteria

**Feature: Memory Management**
```gherkin
Feature: Conversational memory management
  As an AI system
  I want to manage conversation memories
  So that I can maintain relevant context over time

  Background:
    Given the MemoryService is configured
    And all memory messages use the translator with "memory." prefix

  Scenario: Store new memory
    Given a conversation with ID "conv-001"
    And memory content "User prefers detailed technical explanations"
    When I store the memory
    Then the memory should be saved with timestamp
    And it should have a unique generated ID
    And it should be associated with the conversation
    And an embedding should be generated for search
    And success messages should use "memory.service.success.*" translation keys

  Scenario: Retrieve memories by context
    Given multiple stored memories
    And a query "How to explain technical concepts?"
    When I search for relevant memories
    Then I should receive the most similar memories
    And they should be ordered by relevance and recency
    And they should be limited to the requested number
    And retrieval messages should be properly internationalized
```

### Phase 5: MCP Domain

#### 5.1 BDD Acceptance Criteria

**Feature: MCP Tool Management**
```gherkin
Feature: MCP tool management
  As an MCP server
  I want to manage tools dynamically
  So that I can provide flexible capabilities to clients

  Background:
    Given the ToolService is configured
    And all tool messages use the translator with "mcp.tools." prefix

  Scenario: Register new tool
    Given a valid tool definition
    When I register the tool
    Then it should be available for use
    And it should appear in the capabilities list
    And it should have automatically generated documentation
    And registration messages should use "mcp.tools.registration.*" translation keys

  Scenario: Execute tool with validation
    Given a registered tool "search-memory"
    And valid parameters {"query": "machine learning", "limit": 5}
    When I execute the tool
    Then the parameters should be validated
    And the execution should be successful
    And the result should be in the expected format
    And all execution messages should be properly internationalized
```

## QUALITY PIPELINE AND GATES

### Quality Gates by Phase

#### Gate 1: Base Structure
**Mandatory Criteria:**
- [ ] 100% of directories created according to specification
- [ ] All `__init__.py` files with documentation
- [ ] DI system configured and working
- [ ] CI/CD pipeline configured
- [ ] Test coverage > 90%
- [ ] All i18n translation keys validated
- [ ] No hardcoded strings in business logic

#### Gate 2: Embedding Domain
**Mandatory Criteria:**
- [ ] All providers migrated and working
- [ ] Embedding performance < 1s for single text
- [ ] Batch performance < 5s for 100 texts
- [ ] Cache system implemented and tested
- [ ] Test coverage > 95%
- [ ] Quality benchmarks validated
- [ ] All error messages internationalized
- [ ] Translation key coverage validated

#### Gate 3: Knowledge Domain
**Mandatory Criteria:**
- [ ] MEF processing 100% functional
- [ ] UKI validation implemented
- [ ] Search system with filters working
- [ ] Indexing performance > 50 docs/second
- [ ] Search performance < 500ms
- [ ] Test coverage > 95%
- [ ] All MEF validation messages internationalized
- [ ] Translation key coverage validated

#### Gate 4: Memory Domain
**Mandatory Criteria:**
- [ ] Memory management implemented
- [ ] Retrieval strategies working
- [ ] Temporal context implemented
- [ ] Retrieval performance < 200ms
- [ ] Test coverage > 95%
- [ ] All memory messages internationalized
- [ ] Translation key coverage validated

#### Gate 5: MCP Domain
**Mandatory Criteria:**
- [ ] All tools migrated
- [ ] stdio, SSE and HTTP transports working
- [ ] Capabilities system implemented
- [ ] Parameter validation working
- [ ] Test coverage > 95%
- [ ] All tool descriptions internationalized
- [ ] Translation key coverage validated

### Validation Automation

**ci_validation.yml**
```yaml
name: Architecture Validation Pipeline

on: [push, pull_request]

jobs:
  structure_validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Directory Structure
        run: python scripts/validate_structure.py
      - name: Check __init__.py files
        run: find src -name "*.py" -path "*/domains/*" -exec python -m py_compile {} \;

  unit_tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        domain: [embedding, knowledge, memory, mcp]
    steps:
      - uses: actions/checkout@v3
      - name: Run Domain Tests
        run: pytest tests/domains/${{ matrix.domain }}/ -v --cov=synapstor.domains.${{ matrix.domain }}
      - name: Check Coverage
        run: coverage report --fail-under=95

  integration_tests:
    runs-on: ubuntu-latest
    needs: [structure_validation, unit_tests]
    steps:
      - uses: actions/checkout@v3
      - name: Run Integration Tests
        run: pytest tests/integration/ -v
      - name: Performance Tests
        run: pytest tests/performance/ -v

  bdd_tests:
    runs-on: ubuntu-latest
    needs: [integration_tests]
    steps:
      - uses: actions/checkout@v3
      - name: Run BDD Scenarios
        run: behave tests/bdd/
```

### Quality Metrics

**Mandatory Metrics by Phase:**
```yaml
quality_metrics:
  code_coverage:
    minimum: 95%
    target: 98%
  
  performance:
    embedding_generation:
      single_text: "< 1s"
      batch_100: "< 5s"
    search:
      response_time: "< 500ms"
      concurrent_users: 10
    indexing:
      documents_per_second: "> 50"
  
  reliability:
    uptime: "99.9%"
    error_rate: "< 0.1%"
  
  maintainability:
    cyclomatic_complexity: "< 10"
    duplication: "< 5%"
    tech_debt_ratio: "< 5%"
```

### Automated Validation Scripts

**validate_architecture.py**
```python
#!/usr/bin/env python3
"""
Architecture validation script
Executes all necessary verifications for each phase
"""

import os
import subprocess
import yaml
from pathlib import Path

class ArchitectureValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validation_config = self.load_validation_config()
    
    def validate_phase1(self) -> bool:
        """Validate Phase 1 base structure"""
        print("🔍 Validating Phase 1: Base Structure")
        
        # Verify directory structure
        if not self.validate_directory_structure():
            return False
        
        # Verify DI system
        if not self.validate_dependency_injection():
            return False
        
        # Run tests
        if not self.run_tests("tests/phase1/"):
            return False
        
        print("✅ Phase 1 validated successfully!")
        return True
    
    def validate_phase2(self) -> bool:
        """Validate Phase 2 Embedding domain"""
        print("🔍 Validating Phase 2: Embedding Domain")
        
        # Validate performance
        if not self.validate_embedding_performance():
            return False
        
        # Validate quality
        if not self.validate_embedding_quality():
            return False
        
        # Run BDD tests
        if not self.run_bdd_tests("embedding"):
            return False
        
        print("✅ Phase 2 validated successfully!")
        return True
    
    def validate_directory_structure(self) -> bool:
        """Validate if directory structure is correct"""
        required_structure = self.validation_config['directory_structure']
        
        for item in required_structure:
            path = self.project_root / item['path']
            if not path.exists():
                print(f"❌ Directory not found: {path}")
                return False
            
            for required_file in item.get('required_files', []):
                file_path = path / required_file
                if not file_path.exists():
                    print(f"❌ File not found: {file_path}")
                    return False
        
        return True
    
    def run_tests(self, test_path: str) -> bool:
        """Execute tests and verify coverage"""
        cmd = f"pytest {test_path} --cov=synapstor --cov-report=term-missing --cov-fail-under=95"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Tests failed in {test_path}")
            print(result.stdout)
            print(result.stderr)
            return False
        
        return True
    
    def run_bdd_tests(self, domain: str) -> bool:
        """Execute BDD tests for a specific domain"""
        cmd = f"behave tests/bdd/{domain}/ --format=pretty"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ BDD tests failed for {domain}")
            print(result.stdout)
            return False
        
        return True

if __name__ == "__main__":
    validator = ArchitectureValidator(Path.cwd())
    
    phases = [
        validator.validate_phase1,
        validator.validate_phase2,
        # ... other phases
    ]
    
    for i, phase_validator in enumerate(phases, 1):
        if not phase_validator():
            print(f"💥 Validation failed in Phase {i}")
            exit(1)
    
    print("🎉 All phases validated successfully!")
```

This structure ensures that each phase is completely validated before proceeding to the next, with objective quality criteria and automated tests that guarantee the correct functionality of the refactoring.
