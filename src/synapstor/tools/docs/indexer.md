# Indexador para o Qdrant Cloud

Este é um indexador simplificado que se comunica diretamente com o Qdrant Cloud, sem usar o MCP Server como intermediário.
Objetivo é indexar projetos inteiros de uma única vez. essa ferramenta fica disponível quando o usuário instala o synapstor.

## Características:

1. **Comunicação direta**: Usa o cliente Python oficial do Qdrant para comunicação sem intermediários
2. **Incorporação integrada**: Gera embeddings usando o modelo sentence-transformers diretamente  
3. **Instalação automática de dependências**: Verifica e instala as bibliotecas necessárias
4. **Suporte a .gitignore**: Respeita as regras do .gitignore para ignorar arquivos
5. **Processamento em lote**: Agrupa arquivos para envio mais eficiente
6. **Busca semantica**: Permite buscar documentos usando consultas em linguagem natural
7. **Filtros de metadados**: Permite buscar e filtrar por campos de metadados como projeto, extensão, etc.

## Uso:

Para indexar:
```
python indexer.py --project nome-projeto --path /caminho/do/projeto
```