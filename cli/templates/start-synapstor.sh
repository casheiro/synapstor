#!/bin/bash

# Script para iniciar o servidor Synapstor com suporte bilíngue
# Script to start the Synapstor server with bilingual support

# Verificar se existe a variável de ambiente LANG
# Check if the LANG environment variable exists
lang=${LANG:-en_US.UTF-8}

# Detectar idioma preferido
# Detect preferred language
if [[ $lang == *"pt"* ]] || [[ $lang == *"PT"* ]]; then
    echo "Iniciando servidor Synapstor..."
else
    echo "Starting Synapstor server..."
fi

# Iniciar o servidor
# Start the server
synapstor-server
