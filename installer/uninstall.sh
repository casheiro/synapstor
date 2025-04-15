#!/bin/bash

# Script de desinstalação do Synapstor para Linux/macOS
# Autor: Synapstor Team
# Descrição: Remove o Synapstor do sistema, incluindo entradas do PATH,
#            arquivos de configuração e pacote Python

# Cores para mensagens
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_msg() {
    echo -e "${2}${1}${NC}"
}

print_msg "=== Desinstalador do Synapstor ===" "$CYAN"
print_msg "Este script irá remover o Synapstor do seu sistema." "$YELLOW"

# Confirmação do usuário
read -p "Você tem certeza que deseja continuar? (S/N) " confirmacao
if [[ "$confirmacao" != "S" && "$confirmacao" != "s" ]]; then
    print_msg "Desinstalação cancelada." "$YELLOW"
    exit 0
fi

# Função para remover o Synapstor do PATH
remover_do_path() {
    print_msg "\nRemovendo Synapstor do PATH do sistema..." "$CYAN"
    
    # Arquivos de perfil que podem conter configurações do PATH
    arquivos_perfil=(
        "$HOME/.bashrc"
        "$HOME/.bash_profile"
        "$HOME/.profile"
        "$HOME/.zshrc"
    )
    
    for arquivo in "${arquivos_perfil[@]}"; do
        if [ -f "$arquivo" ]; then
            print_msg "Verificando $arquivo..." "$YELLOW"
            
            # Backup do arquivo original
            cp "$arquivo" "${arquivo}.synapstor_backup"
            
            # Remover linhas que adicionam Synapstor ao PATH
            sed -i.bak '/synapstor/d' "$arquivo"
            
            # Verificar se houve alterações
            if diff "$arquivo" "${arquivo}.synapstor_backup" > /dev/null; then
                print_msg "Nenhuma alteração em $arquivo" "$YELLOW"
                rm "${arquivo}.synapstor_backup"
            else
                print_msg "PATH atualizado em $arquivo" "$GREEN"
            fi
            
            # Remover arquivo .bak
            rm -f "${arquivo}.bak"
        fi
    done
    
    print_msg "Para aplicar as alterações no PATH, feche e reabra o terminal ou execute 'source ~/.bashrc' (ou equivalente)." "$YELLOW"
}

# Função para remover arquivos de configuração
limpar_arquivos_configuracao() {
    print_msg "\nRemovendo arquivos de configuração..." "$CYAN"
    
    # Locais comuns para arquivos de configuração
    config_dirs=(
        "$HOME/.config/synapstor"
        "$HOME/.synapstor"
    )
    
    for dir in "${config_dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_msg "Removendo $dir..." "$YELLOW"
            rm -rf "$dir"
            print_msg "Removido: $dir" "$GREEN"
        fi
    done
    
    # Verificar arquivos de configuração do Cursor
    cursor_config="$HOME/.cursor/mcp.json"
    if [ -f "$cursor_config" ]; then
        print_msg "Arquivo de configuração do Cursor detectado em: $cursor_config" "$YELLOW"
        print_msg "Recomendamos verificar manualmente este arquivo para remover configurações do Synapstor." "$YELLOW"
    fi
}

# Função para desinstalar o pacote Python
desinstalar_pacote() {
    print_msg "\nDesinstalando o pacote Synapstor..." "$CYAN"
    
    # Verificar diferentes comandos pip (pip, pip3)
    pip_commands=("pip" "pip3")
    desinstalado=false
    
    for pip_cmd in "${pip_commands[@]}"; do
        if command -v "$pip_cmd" > /dev/null; then
            print_msg "Usando $pip_cmd para desinstalar..." "$YELLOW"
            
            # Tentar desinstalar
            if $pip_cmd uninstall -y synapstor; then
                print_msg "Pacote Synapstor desinstalado com sucesso usando $pip_cmd." "$GREEN"
                desinstalado=true
                break
            fi
        fi
    done
    
    if [ "$desinstalado" = false ]; then
        print_msg "Não foi possível desinstalar o pacote Synapstor automaticamente." "$RED"
        print_msg "Execute manualmente: pip uninstall -y synapstor" "$YELLOW"
    fi
}

# Executar etapas de desinstalação
remover_do_path
limpar_arquivos_configuracao
desinstalar_pacote

print_msg "\nDesinstalação concluída." "$GREEN"
print_msg "Obrigado por usar o Synapstor!" "$CYAN"

# Aguardar antes de sair
read -p "Pressione ENTER para sair..." 