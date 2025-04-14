#!/bin/bash

# Script para iniciar o servidor MCP Qdrant no Linux/macOS

echo "Iniciando servidor MCP Qdrant..."

# Preparando argumentos
ARGS=("scripts/start_server.py")

# Processando argumentos de linha de comando
TRANSPORT="sse"
ENV_FILE=".env"
CREATE_ENV=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --transport)
      TRANSPORT="$2"
      shift 2
      ;;
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    --create-env)
      CREATE_ENV=true
      shift
      ;;
    *)
      echo "Argumento desconhecido: $1"
      shift
      ;;
  esac
done

# Adicionando os argumentos processados
ARGS+=("--transport" "$TRANSPORT")
if [[ "$ENV_FILE" != ".env" ]]; then
  ARGS+=("--env-file" "$ENV_FILE")
fi
if [[ "$CREATE_ENV" == true ]]; then
  ARGS+=("--create-env")
fi

# Executando o script Python
python3 "${ARGS[@]}"

# Verifica se houve erro
if [ $? -ne 0 ]; then
  echo "Erro ao iniciar o servidor"
  read -p "Pressione Enter para continuar..."
else
  echo "Servidor iniciado com sucesso. Pressione Ctrl+C para finalizar."
fi 