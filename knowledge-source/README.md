# Synapstor Knowledge Base

This directory contains business-focused knowledge documentation structured according to the Matrix Embedding Framework (MEF) specification.

## Directory Structure

```
knowledge-source/
├── business/     # Business rules, processes, and models
├── product/      # Product guidelines, user workflows, and design patterns
├── strategy/     # Strategic decisions and architectural choices
├── culture/      # Team processes, cultural practices, and guidelines
└── technical/    # (Future) Technical patterns and implementation details
```

## Knowledge Domains

### Business Domain
Contains UKIs focused on business rules, policies, and operational models:
- MEF validation and processing rules
- MCP integration business model
- Knowledge indexing and storage policies

### Product Domain  
Contains UKIs focused on user experience, interface design, and product workflows:
- CLI interface design guidelines
- Knowledge search user experience patterns
- MEF document authoring workflows

### Strategy Domain
Contains UKIs documenting strategic decisions and long-term planning:
- MCP protocol adoption rationale
- MEF knowledge framework strategy
- Open source positioning and community strategy

### Culture Domain
Contains UKIs focused on team practices, processes, and cultural standards:
- Conventional commits and automated release practices
- Internationalization development guidelines
- Open source contribution standards

## Using This Knowledge Base

### For Developers
These UKIs provide context for understanding business requirements, design decisions, and implementation guidelines. Use them to:
- Understand the reasoning behind technical choices
- Learn about business rules that affect implementation
- Follow established patterns and practices

### For Product Teams
These UKIs document product decisions, user workflows, and design guidelines. Use them to:
- Maintain consistency in product decisions
- Understand user experience patterns
- Reference established design guidelines

### For Business Teams
These UKIs capture business rules, processes, and strategic decisions. Use them to:
- Understand operational policies
- Reference strategic rationale for decisions
- Maintain consistency in business processes

### For Community Contributors
These UKIs help new contributors understand project culture, processes, and standards. Use them to:
- Learn contribution guidelines and standards
- Understand project governance and decision-making
- Reference development practices and workflows

## Indexing with MEF

To index this knowledge base with Synapstor's MEF support:

```bash
# Enable MEF processing
synapstor-indexer --project synapstor-knowledge --path ./knowledge-source -m

# Strict validation mode
synapstor-indexer --project synapstor-knowledge --path ./knowledge-source -m -e
```

## Maintaining This Knowledge Base

### Adding New UKIs
1. Determine appropriate domain (business, product, strategy, culture)
2. Follow MEF specification for structure and metadata
3. Use descriptive IDs following `unik-[domain]-[descriptive-name]` pattern
4. Include relevant examples and relationships
5. Validate using MEF validation tools

### Updating Existing UKIs
1. Update `last_validation` date when reviewing content
2. Ensure `related_to` links remain accurate
3. Update examples if underlying systems change
4. Maintain consistency with related UKIs

### Quality Standards
- Content should be actionable and practical
- Examples should be realistic and current
- Language should be clear and accessible
- Relationships should be meaningful and maintained

## Integration with Development Workflow

This knowledge base is designed to be indexed by Synapstor and made available to LLMs through MCP integration, enabling:
- Contextual assistance during development
- Automated discovery of relevant business rules
- Consistent application of established patterns
- Knowledge sharing across team boundaries

## Contributing

When contributing to this knowledge base:
1. Follow MEF specification requirements
2. Ensure content is business/product focused (not technical implementation)
3. Include practical examples and clear intent of use
4. Link to related UKIs where appropriate
5. Update validation dates when reviewing content

For technical implementation details, see the main Synapstor documentation and codebase.
