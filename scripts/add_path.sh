#!/bin/bash
# Script para adicionar o diretório de scripts do Python ao PATH no Linux/macOS
# Este script é executado durante a instalação do Synapstor

echo "Adicionando comandos do Synapstor ao PATH..."

# Determina o diretório de scripts do Python
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPTS="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Diretório detectado: $PYTHON_SCRIPTS"

# Verifica se o diretório existe
if [ ! -d "$PYTHON_SCRIPTS" ]; then
    echo "Erro: O diretório $PYTHON_SCRIPTS não existe."
    exit 1
fi

# Determina o shell do usuário
USER_SHELL="${SHELL:-/bin/bash}"
HOME_DIR="$HOME"

# Define os arquivos de configuração baseados no shell
CONFIG_FILE=""

case "$USER_SHELL" in
    */bash)
        if [ -f "$HOME_DIR/.bashrc" ]; then
            CONFIG_FILE="$HOME_DIR/.bashrc"
        elif [ -f "$HOME_DIR/.bash_profile" ]; then
            CONFIG_FILE="$HOME_DIR/.bash_profile"
        fi
        ;;
    */zsh)
        if [ -f "$HOME_DIR/.zshrc" ]; then
            CONFIG_FILE="$HOME_DIR/.zshrc"
        fi
        ;;
    */fish)
        if [ -d "$HOME_DIR/.config/fish" ]; then
            CONFIG_FILE="$HOME_DIR/.config/fish/config.fish"
        fi
        ;;
    *)
        # Fallback para .profile
        CONFIG_FILE="$HOME_DIR/.profile"
        ;;
esac

# Se o arquivo de configuração não foi encontrado, usa .profile
if [ -z "$CONFIG_FILE" ] || [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="$HOME_DIR/.profile"
    # Cria o arquivo se não existir
    if [ ! -f "$CONFIG_FILE" ]; then
        touch "$CONFIG_FILE"
    fi
fi

echo "Usando arquivo de configuração: $CONFIG_FILE"

# Prepara a linha de exportação de PATH
EXPORT_LINE="# Adicionado pelo Synapstor"
EXPORT_LINE2="export PATH=\"\$PATH:$PYTHON_SCRIPTS\""

# Verifica se o diretório já está no PATH
if grep -q "$PYTHON_SCRIPTS" "$CONFIG_FILE"; then
    echo "✅ O diretório já está configurado no PATH."
else
    # Adiciona ao arquivo de configuração
    echo "" >> "$CONFIG_FILE"
    echo "$EXPORT_LINE" >> "$CONFIG_FILE"
    echo "$EXPORT_LINE2" >> "$CONFIG_FILE"
    echo "" >> "$CONFIG_FILE"
    echo "✅ Caminho adicionado a $CONFIG_FILE"
fi

# Instruções para o usuário
echo ""
echo "IMPORTANTE: Para aplicar as alterações, execute:"
echo "  source $CONFIG_FILE"
echo ""
echo "Ou reinicie seu terminal."

# Tenta aplicar as alterações imediatamente
if [ -f "$CONFIG_FILE" ]; then
    echo "Tentando aplicar as alterações automaticamente..."
    source "$CONFIG_FILE" 2>/dev/null || . "$CONFIG_FILE" 2>/dev/null
fi

echo ""
echo "Configuração concluída!" 