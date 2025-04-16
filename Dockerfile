FROM python:3.11-slim

WORKDIR /app

# Instala dependências essenciais
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clona o repositório do Synapstor
# Substitua o URL do repositório pelo correto quando disponível
RUN git clone https://github.com/seu-usuario/synapstor.git .

# Instala o pacote em modo de desenvolvimento
RUN pip install --no-cache-dir -e .

# Expõe a porta padrão para transporte SSE
EXPOSE 8000

# Define variáveis de ambiente com valores padrão que podem ser sobrescritos em tempo de execução
ENV QDRANT_URL=""
ENV QDRANT_API_KEY=""
ENV COLLECTION_NAME="synapstor"
ENV EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Executa o servidor com transporte SSE usando o synapstor-ctl (interface recomendada)
CMD ["synapstor-ctl", "server", "--transport", "sse"]
