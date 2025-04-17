# Synapstor 📚🔍

<p align="center">
  <img src="https://2.gravatar.com/userimage/264864229/4e133a67b7d5fff345dd8f2bc4d0743b?size=400" alt="Synapstor" width="400"/>
</p>

![Version](https://img.shields.io/badge/versão-0.1.2-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/licença-MIT-green)

> **Synapstor** é uma biblioteca modular para armazenamento e recuperação semântica de informações usando embeddings vetoriais e banco de dados Qdrant.
>
> **Nota**: O Synapstor é uma evolução não oficial do projeto [mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant), expandindo suas funcionalidades para criar uma solução mais abrangente para armazenamento e recuperação semântica.


## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Ferramentas CLI](#-ferramentas-cli)
- [Uso Rápido](#-uso-rápido)
- [Integração com LLMs](#-integração-com-llms)
- [Deployment com Docker](#-deployment-com-docker)
- [Documentação Detalhada](#-documentação-detalhada)
- [Testes](#-testes)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## 🔭 Visão Geral

Synapstor é uma solução completa para armazenamento e recuperação de informações baseada em embeddings vetoriais. Combinando a potência do Qdrant (banco de dados vetorial) com modelos modernos de embeddings, o Synapstor permite:

- 🔍 **Busca semântica** em documentos, código e outros conteúdos textuais
- 🧠 **Armazenamento eficiente** de informações com metadados associados
- 🔄 **Integração com LLMs** através do Protocolo MCP (Model Control Protocol)
- 🛠️ **Ferramentas CLI** para indexação e consulta de dados

O projeto foi desenhado com modularidade e extensibilidade em mente, permitindo fácil customização e ampliação de suas capacidades.

## 🏗️ Arquitetura

A estrutura real do projeto é organizada da seguinte forma:

```
synapstor/
├── src/
│   └── synapstor/           # Pacote principal
│       ├── embeddings/      # Geradores de embeddings vetoriais
│       ├── plugins/         # Sistema de plugins extensível
│       ├── tools/           # Utilitários e ferramentas CLI
│       ├── utils/           # Funções auxiliares
│       ├── qdrant.py        # Conector para o banco de dados Qdrant
│       ├── settings.py      # Configurações do sistema
│       ├── mcp_server.py    # Implementação do servidor MCP
│       ├── main.py          # Ponto de entrada principal
│       ├── server.py        # Implementação do servidor
│       └── env_loader.py    # Carregador de variáveis de ambiente
├── tests/                   # Testes automatizados
└── pyproject.toml           # Configuração do projeto e dependências
```

## 🖥️ Requisitos

### Dependências Principais

- **Python**: 3.10 ou superior
- **Qdrant**: Banco de dados vetorial para armazenamento e busca de embeddings
- **Modelos de Embedding**: Por padrão, usa modelos da biblioteca FastEmbed

### Requisitos para o Qdrant

O Synapstor funciona com o Qdrant de duas formas:

1. **Qdrant Cloud** (Recomendado para produção):
   - Crie uma conta em [cloud.qdrant.io](https://cloud.qdrant.io/)
   - Obtenha sua URL e chave API
   - Configure o Synapstor com estas credenciais

2. **Qdrant Local** (Recomendado para desenvolvimento):
   - **Docker** (mais simples):
     ```bash
     docker pull qdrant/qdrant
     docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
     ```
   - **Instalação nativa**: Consulte a [documentação oficial do Qdrant](https://qdrant.tech/documentation/guides/installation/)

## 📦 Instalação

### Ambiente Virtual (Recomendado)

É altamente recomendado usar um ambiente virtual para evitar conflitos de dependências.

#### Usando Conda (Recomendado)

```bash
# Instalar Conda (se ainda não tiver)
# Visite https://docs.conda.io/en/latest/miniconda.html

# Criar ambiente virtual
conda create -n synapstor python=3.10
conda activate synapstor

# Clone o repositório
git clone https://github.com/casheiro/synapstor.git
cd synapstor

# Instalação básica (apenas pacote principal)
pip install -e .

# Instalação para desenvolvimento (inclui formatadores e linters)
pip install -e ".[dev]"

# Instalação para testes (inclui pytest e plugins)
pip install -e ".[test]"

# Instalação completa (desenvolvimento, testes e recursos opcionais)
pip install -e ".[all]"
```

#### Usando venv

```bash
# Criar ambiente virtual
python -m venv synapstor-env
source synapstor-env/bin/activate  # Linux/macOS
# ou
synapstor-env\Scripts\activate  # Windows

# Clone o repositório
git clone https://github.com/casheiro/synapstor.git
cd synapstor

# Instalação básica (apenas pacote principal)
pip install -e .

# Instalação para desenvolvimento (inclui formatadores e linters)
pip install -e ".[dev]"

# Instalação para testes (inclui pytest e plugins)
pip install -e ".[test]"

# Instalação completa (desenvolvimento, testes e recursos opcionais)
pip install -e ".[all]"
```

### Instalação via PyPI (para usuários)

```bash
# Instalação básica
pip install synapstor

# Com suporte a fastembed (recomendado para embeddings rápidos)
pip install "synapstor[fastembed]"
```

### Instalação de Dependências de Desenvolvimento

Se você precisa executar testes ou contribuir com o desenvolvimento, instale as dependências de teste manualmente:

```bash
# Dentro do diretório do projeto, com ambiente virtual ativado
pip install pytest pytest-cov
```

## 🔧 Ferramentas CLI

O Synapstor oferece um conjunto de ferramentas de linha de comando para facilitar seu uso. A forma mais recomendada de interagir com o Synapstor é através do comando centralizado `synapstor-ctl`.

### `synapstor-ctl` (Recomendado)

Interface centralizada para gerenciar todas as funcionalidades do Synapstor:

```bash
# Iniciar o servidor MCP
synapstor-ctl server

# Configuração interativa
synapstor-ctl configure

# Indexar um projeto
synapstor-ctl indexer --project meu-projeto --path /caminho/do/projeto

# Ver status
synapstor-ctl status

# Listar coleções disponíveis
synapstor-ctl collections list

# Ajuda sobre comandos disponíveis
synapstor-ctl --help
```

### Ferramentas Individuais

Além do `synapstor-ctl`, você também pode usar as ferramentas individuais:

#### `synapstor-server`

Inicia o servidor MCP para integração com LLMs e outras ferramentas.

```bash
# Uso básico
synapstor-server

# Especificar protocolo de transporte
synapstor-server --transport sse

# Especificar arquivo .env personalizado
synapstor-server --env-file config.env
```

#### `synapstor-indexer`

Ferramenta para indexação em lote de projetos e diretórios no Qdrant.

```bash
# Indexar um projeto completo
synapstor-indexer --project meu-projeto --path /caminho/do/projeto

# Opções avançadas
synapstor-indexer --project meu-projeto --path /caminho/do/projeto \
  --collection colecao-personalizada \
  --workers 8 \
  --max-file-size 5 \
  --verbose

# Indexar e testar com uma consulta
synapstor-indexer --project meu-projeto --path /caminho/do/projeto \
  --query "como implementar autenticação"
```

A ferramenta de indexação oferece funcionalidades avançadas:
- Respeito a regras `.gitignore` para exclusão de arquivos
- Detecção automática de arquivos binários
- Processamento paralelo para indexação rápida
- IDs determinísticos para evitar duplicação de documentos

## 🚀 Uso Rápido

### Configuração

Configure o Synapstor através de variáveis de ambiente ou arquivo `.env`:

```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=sua-chave-api
COLLECTION_NAME=synapstor
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Exemplos de Uso

#### Como servidor MCP

```bash
# Iniciar o servidor MCP com a interface centralizada
synapstor-ctl server

# Ou usando o comando específico
synapstor-server
```

#### Indexação de projetos

```bash
# Indexar um projeto usando a interface centralizada (recomendado)
synapstor-ctl indexer --project meu-projeto --path /caminho/do/projeto

# Ou usando o comando específico
synapstor-indexer --project meu-projeto --path /caminho/do/projeto
```

#### Como biblioteca em aplicações Python

```python
from synapstor.qdrant import QdrantConnector, Entry
from synapstor.embeddings.factory import create_embedding_provider
from synapstor.settings import EmbeddingProviderSettings

# Inicializar componentes
settings = EmbeddingProviderSettings()
embedding_provider = create_embedding_provider(settings)

connector = QdrantConnector(
    qdrant_url="http://localhost:6333",
    collection_name="minha_colecao",
    embedding_provider=embedding_provider
)

# Armazenar informações
async def store_data():
    entry = Entry(
        content="Conteúdo a ser armazenado",
        metadata={"chave": "valor"}
    )
    await connector.store(entry)

# Buscar informações
async def search_data():
    results = await connector.search("consulta em linguagem natural")
    for result in results:
        print(result.content)
```

## 🤖 Integração com LLMs

O Synapstor implementa o [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction), permitindo integração com diversos modelos de linguagem.

### 1. Integração com Claude (Anthropic)

#### Claude Desktop

Configure o Synapstor no arquivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "synapstor": {
      "command": "synapstor-ctl",
      "args": ["server", "--transport", "stdio"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "minha-colecao",
        "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
      }
    }
  }
}
```

#### Claude Web / API

Inicie o servidor com transporte SSE:

```bash
synapstor-ctl server --transport sse
```

Acesse via API Anthropic usando o endpoint local do Synapstor como provedor MCP.

### 2. Integração com Cursor (Editor de Código)

1. Inicie o servidor MCP:
   ```bash
   synapstor-ctl server --transport sse
   ```

2. Em Cursor, vá para Configurações → Contexto → Adicionar Servidor MCP
3. Configure a URL: `http://localhost:8000/sse`
4. Personalize as descrições de ferramenta para melhor integração com seu fluxo de trabalho

### 3. Integração com Windsurf

Semelhante ao Cursor, configure o Windsurf para usar o endpoint SSE do Synapstor como provedor MCP.

### 4. Integração com Microsoft Copilot

Para integrar com Microsoft Copilot:

1. Inicie o servidor com configurações específicas:
   ```bash
   TOOL_STORE_DESCRIPTION="Armazene trechos de código ou documentação" \
   TOOL_FIND_DESCRIPTION="Busque informações relacionadas à consulta" \
   synapstor-ctl server --transport stdio
   ```

2. Configure o Copilot para usar o Synapstor como provedor de plugins

## 🐳 Deployment com Docker

O Synapstor pode ser facilmente implantado usando Docker, permitindo uma configuração consistente em diferentes ambientes.

### Dockerfile Incluído

O projeto inclui um Dockerfile pré-configurado que:
- Usa Python 3.11 como base
- Clona o repositório do Synapstor
- Configura as dependências necessárias
- Expõe a porta 8000 para o transporte SSE
- Usa `synapstor-ctl` como ponto de entrada

### Construindo a Imagem Docker

```bash
# Na raiz do projeto (onde está o Dockerfile)
docker build -t synapstor .
```

### Executando o Contêiner

```bash
# Executar com as configurações básicas
docker run -p 8000:8000 synapstor

# Executar com variáveis de ambiente personalizadas
docker run -p 8000:8000 \
  -e QDRANT_URL="http://seu-servidor-qdrant:6333" \
  -e QDRANT_API_KEY="sua-chave-api" \
  -e COLLECTION_NAME="sua-colecao" \
  -e EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \
  synapstor
```

### Conectando a um Qdrant Externo

Para conectar o contêiner Synapstor a um Qdrant executando em outro contêiner ou serviço:

```bash
# Criar uma rede Docker
docker network create synapstor-network

# Executar o Qdrant
docker run -d --name qdrant --network synapstor-network \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Executar o Synapstor conectado ao Qdrant
docker run -d --name synapstor --network synapstor-network \
  -p 8000:8000 \
  -e QDRANT_URL="http://qdrant:6333" \
  -e COLLECTION_NAME="synapstor" \
  synapstor
```

### Docker Compose (Recomendado para Desenvolvimento)

Para uma configuração completa com Qdrant e Synapstor, você pode usar Docker Compose:

```yaml
# docker-compose.yml
version: '3'

services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    networks:
      - synapstor-network

  synapstor:
    build: .
    ports:
      - "8000:8000"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - COLLECTION_NAME=synapstor
      - EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
    depends_on:
      - qdrant
    networks:
      - synapstor-network

networks:
  synapstor-network:
```

Para usar:

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar todos os serviços
docker-compose down
```

## 📚 Documentação Detalhada

O Synapstor possui documentação específica para cada módulo:

- **[Módulo Principal](src/synapstor/README.md)**: Visão geral e componentes principais
- **[Embeddings](src/synapstor/embeddings/README.md)**: Geração de embeddings vetoriais
- **[Plugins](src/synapstor/plugins/README.md)**: Sistema extensível de plugins
- **[Ferramentas](src/synapstor/tools/README.md)**: Ferramentas CLI e utilitários
- **[Utilitários](src/synapstor/utils/README.md)**: Funções auxiliares comuns
- **[Testes](tests/README.md)**: Suíte de testes e exemplos

## 🧪 Testes

O Synapstor inclui uma suíte completa de testes para garantir a qualidade e robustez do código:

```bash
# Com ambiente virtual ativado e dependências de teste instaladas (pip install -e ".[test]")

# Executar todos os testes
pytest

# Executar um módulo específico de testes
pytest tests/test_qdrant_integration.py

# Executar com cobertura de código
pytest --cov=synapstor
```

### Integração Contínua

O projeto utiliza GitHub Actions para automatizar testes, verificações de qualidade de código e publicação:

- **Testes Automatizados**: Executa os testes em múltiplas versões do Python (3.10, 3.11, 3.12)
- **Pre-commit Checks**: Verifica formatação, linting e tipagem estática
- **Publicação de Pacotes**: Automatiza o processo de publicação no PyPI

Você pode ver os detalhes nas configurações em `.github/workflows/`.

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir para o Synapstor:

1. Faça um fork do projeto
2. Configure seu ambiente de desenvolvimento:
   ```bash
   # Clone seu fork
   git clone https://github.com/seu-usuario/synapstor.git
   cd synapstor

   # Instale as dependências de desenvolvimento
   pip install -e ".[dev,test]"

   # Configure o pre-commit
   pre-commit install
   ```
3. Crie uma branch para sua feature (`git checkout -b feature/nome-da-feature`)
4. Faça suas alterações seguindo as convenções do projeto
5. Execute os testes para garantir que tudo está funcionando (`pytest`)
6. Faça commit e push das alterações (`git push origin feature/nome-da-feature`)
7. Abra um Pull Request descrevendo suas alterações

### Fluxo de Desenvolvimento

- Mantenha os commits pequenos e focados
- Escreva testes para novas funcionalidades
- Siga o estilo de código do projeto (enforçado pelo pre-commit)
- Mantenha a documentação atualizada
- Atualize o CHANGELOG.md para novas versões

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  Desenvolvido com ❤️ pelo time Synapstor by <a href="https://github.com/casheiro">Casheiro®</a>
</p>
