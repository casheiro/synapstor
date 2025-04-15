#!/bin/bash
# Script rápido para desinstalar o Synapstor em Linux/macOS

echo "Desinstalador rápido do Synapstor"
echo "==============================="

# Possíveis caminhos do Python
PYTHON_PATHS=(
    "/usr/bin/python3"
    "/usr/local/bin/python3"
    "/opt/homebrew/bin/python3"
    "$HOME/.pyenv/shims/python3"
    "$HOME/miniconda3/bin/python3"
    "$HOME/anaconda3/bin/python3"
    "/usr/bin/python"
    "/usr/local/bin/python"
)

# Tenta usar o Python do PATH
if command -v python3 &> /dev/null; then
    echo "Usando python3 do PATH"
    python3 -m pip uninstall -y synapstor
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        echo -e "\nSynapstor desinstalado com sucesso!"
        read -p "Pressione ENTER para sair..."
        exit 0
    fi
fi

# Tenta usar o Python do PATH
if command -v python &> /dev/null; then
    echo "Usando python do PATH"
    python -m pip uninstall -y synapstor
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        echo -e "\nSynapstor desinstalado com sucesso!"
        read -p "Pressione ENTER para sair..."
        exit 0
    fi
fi

# Tenta cada caminho possível
for py_path in "${PYTHON_PATHS[@]}"; do
    if [ -f "$py_path" ]; then
        echo "Usando Python: $py_path"
        "$py_path" -m pip uninstall -y synapstor
        RESULT=$?
        if [ $RESULT -eq 0 ]; then
            echo -e "\nSynapstor desinstalado com sucesso!"
            read -p "Pressione ENTER para sair..."
            exit 0
        fi
    fi
done

# Tenta usar pip diretamente
if command -v pip3 &> /dev/null; then
    echo "Usando pip3 do PATH"
    pip3 uninstall -y synapstor
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        echo -e "\nSynapstor desinstalado com sucesso!"
        read -p "Pressione ENTER para sair..."
        exit 0
    fi
fi

if command -v pip &> /dev/null; then
    echo "Usando pip do PATH"
    pip uninstall -y synapstor
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        echo -e "\nSynapstor desinstalado com sucesso!"
        read -p "Pressione ENTER para sair..."
        exit 0
    fi
fi

echo "Não foi possível encontrar Python ou pip no sistema."
echo "Por favor, desinstale o Synapstor manualmente usando o comando:"
echo "pip uninstall -y synapstor"

read -p "Pressione ENTER para sair..." 