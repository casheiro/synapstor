FROM python:3.11-slim

WORKDIR /app

# Install essential dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the Synapstor repository
# Replace the repository URL with the correct one when available
RUN git clone https://github.com/casheiro/synapstor.git .

# Install the package in development mode
RUN pip install --no-cache-dir -e .

# Expose the default port for SSE transport
EXPOSE 8000

# Define environment variables with default values that can be overridden at runtime
ENV QDRANT_URL=""
ENV QDRANT_API_KEY=""
ENV COLLECTION_NAME="synapstor"
ENV EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Run the server with SSE transport using synapstor-ctl (recommended interface)
CMD ["synapstor-ctl", "server", "--transport", "sse"]
