pt_BR

# Configuração do Projeto Gemini

## Visão Geral do Projeto

Este projeto, `synapstor`, é uma biblioteca modular para armazenamento e recuperação semântica de informações usando embeddings vetoriais e o banco de dados Qdrant. Ele fornece ferramentas para indexar conteúdo, executar um servidor para busca semântica e integrar com Modelos de Linguagem Grandes (LLMs).

## Estrutura de Arquivos e Diretórios

O projeto está organizado em vários diretórios chave:

- `src/synapstor`: Contém o código-fonte principal em Python para a biblioteca `synapstor`.
- `cli`: Contém as ferramentas de linha de comando (CLI) para interagir com o `synapstor`.
- `tests`: Contém os testes para o projeto.
- `.github/workflows`: Contém os fluxos de trabalho do GitHub Actions para integração contínua e deployment.

## Tecnologias Principais

- **Linguagem de Programação**: Python (>=3.10)
- **Banco de Dados Vetorial**: Qdrant
- **Modelos de Embedding**: Utiliza primariamente modelos das bibliotecas `fastembed` e `sentence-transformers`.
- **Framework de CLI**: `docopt` e scripts customizados.
- **Framework Web**: `fastapi` e `uvicorn` para o componente do servidor.

## Comandos e Scripts Chave

O projeto utiliza um conjunto de ferramentas de linha de comando customizadas para várias tarefas. Aqui estão algumas das mais importantes:

### `synapstor-ctl`

Este é o principal script de controle para gerenciar o serviço `synapstor`.

- **`synapstor-ctl start`**: Inicia o servidor `synapstor` em segundo plano.
- **`synapstor-ctl stop`**: Para o servidor `synapstor`.
- **`synapstor-ctl status`**: Verifica o status do servidor `synapstor`.
- **`synapstor-ctl logs`**: Exibe os logs do servidor `synapstor`.
- **`synapstor-ctl reindex`**: Reindexa um projeto.

### `synapstor-indexer`

Este script é usado para indexar conteúdo no banco de dados Qdrant.

- **`synapstor-indexer --project <nome_do_projeto> --path <caminho_para_o_projeto>`**: Indexa o conteúdo de um projeto.

### `synapstor-server`

Este script executa o servidor `synapstor`, que fornece uma API para busca semântica.

- **`synapstor-server --transport sse`**: Executa o servidor com transporte Server-Sent Events (SSE).

### `synapstor-setup`

Este script é usado para a configuração inicial do ambiente `synapstor`.

- **`synapstor-setup`**: Executa um processo de configuração interativo.

## Fluxo de Desenvolvimento

O projeto usa `pre-commit` para garantir a qualidade e o estilo do código. A configuração para o `pre-commit` está em `.pre-commit-config.yaml`.

### Configurando o Ambiente de Desenvolvimento

1.  **Clone o repositório**:
    ```bash
    git clone https://github.com/casheiro/synapstor.git
    cd synapstor
    ```

2.  **Crie um ambiente virtual**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências**:
    ```bash
    pip install -e ".[dev,test]"
    ```

4.  **Configure os hooks do pre-commit**:
    ```bash
    pre-commit install
    ```

### Executando Testes

Para executar a suíte de testes do projeto:

```bash
pytest
```

### Commitando Alterações

O projeto usa `commitizen` para forçar o uso de mensagens de commit convencionais. Para commitar alterações:

```bash
cz commit
```

Isso o guiará na criação de uma mensagem de commit compatível.

## Integração com LLMs

O `synapstor` é projetado para se integrar com Modelos de Linguagem Grandes (LLMs) como o Claude e outros. O componente de servidor fornece uma API que pode ser usada para alimentar contexto aos LLMs, permitindo que eles respondam a perguntas com base no conteúdo indexado.

### Exemplo de Integração com o Claude

Para integrar com o Claude, você normalmente o configuraria para usar o servidor `synapstor` como um provedor de contexto. Isso permite que o Claude acesse as informações indexadas e forneça respostas mais relevantes e precisas.

## Deployment

O projeto inclui um `Dockerfile` para deployment em contêiner.

### Construindo a Imagem Docker

```bash
docker build -t synapstor .
```

### Executando o Contêiner Docker

```bash
docker run -p 8000:8000 -e QDRANT_URL=<sua_url_qdrant> synapstor
```

Isso iniciará o servidor `synapstor`, tornando-o acessível na porta 8000. Você pode então configurar seus LLMs ou outras aplicações para usar este servidor para busca e recuperação semântica.
