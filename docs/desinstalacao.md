# Guia de Desinstalação do Synapstor

Este documento explica em detalhes as diferentes formas de desinstalar o Synapstor do seu sistema.

## Visão Geral

O Synapstor foi projetado para facilitar sua remoção, oferecendo múltiplas opções adaptadas a diferentes ambientes e níveis de experiência. Você pode escolher a que melhor se adequar às suas necessidades:

| Método | Descrição | Confirmação | Ambiente | Nível |
|--------|-----------|-------------|----------|-------|
| `synapstor-remove` | Comando Python direto sem confirmação | Não | Todos | Básico |
| `uninstall-synapstor` | Alias para desinstalação rápida | Não | Todos | Básico |
| `synapstor-uninstall` | Comando com confirmação interativa | Sim | Todos | Intermediário |
| `synapstorctl uninstall` | Via gerenciador central com confirmação | Sim | Todos | Intermediário |
| Scripts universais | Scripts independentes para desinstalação | Não | Específico do SO | Avançado |

## Métodos de Desinstalação

### 1. Desinstalação Rápida (Sem Confirmação)

Este método é ideal para automação e usuários que já sabem o que estão fazendo:

```bash
# Opção 1 (recomendada)
synapstor-remove

# Opção 2 (alias)
uninstall-synapstor
```

Estes comandos:
- Não solicitam confirmação
- Executam a desinstalação imediatamente
- Removem apenas o pacote Python (não limpam configurações ou entradas do PATH)

### 2. Desinstalação com Confirmação

Estes métodos solicitam confirmação antes de prosseguir:

```bash
# Via comando Python direto
synapstor-uninstall

# Via gerenciador central (mais completo)
synapstorctl uninstall
```

O comando `synapstorctl uninstall`:
- Solicita confirmação do usuário
- Remove o pacote Python
- Limpa entradas do PATH (quando possível)
- Remove arquivos de configuração

### 3. Scripts Universais de Desinstalação

Para situações em que os métodos anteriores não estão disponíveis (PATH não configurado ou problemas de ambiente), use os scripts universais incluídos no pacote:

**Windows:**
```bash
# No PowerShell ou Prompt de Comando
.\quick-uninstall.bat
```

**Linux/macOS:**
```bash
# Tornar executável e rodar
chmod +x quick-uninstall.sh
./quick-uninstall.sh
```

Estes scripts:
- Funcionam sem depender do PATH
- Tentam múltiplos caminhos comuns para encontrar o Python
- São úteis em ambientes restritos ou configurações problemáticas

## Desinstalação Manual

Se nenhum dos métodos automáticos funcionar, você pode sempre desinstalar manualmente:

```bash
# Usando pip diretamente
pip uninstall -y synapstor

# Ou especificando o Python a ser usado
python -m pip uninstall -y synapstor
python3 -m pip uninstall -y synapstor
```

## Limpeza Adicional

Após a desinstalação, você pode querer limpar manualmente:

### Arquivos de Configuração

Os arquivos de configuração podem estar em:

**Windows:**
- `%APPDATA%\Synapstor\`
- `%LOCALAPPDATA%\Synapstor\`
- `%USERPROFILE%\.cursor\mcp.json` (configuração do Cursor)

**Linux/macOS:**
- `~/.config/synapstor/`
- `~/.synapstor/`
- `~/.cursor/mcp.json` (configuração do Cursor)

### Entradas no PATH

Dependendo de como você instalou o Synapstor, pode haver entradas no PATH que você deseje remover:

**Windows:**
- Edite as variáveis de ambiente através do Painel de Controle
- Remova manualmente quaisquer entradas contendo "synapstor"

**Linux/macOS:**
- Verifique e edite:
  - `~/.bashrc`
  - `~/.bash_profile`
  - `~/.zshrc`
  - `~/.profile`
- Remova linhas que adicionam o Synapstor ao PATH

## Problemas Comuns

### Arquivo ou comando não encontrado

Se você receber um erro como "comando não encontrado", tente:

1. Verificar se o diretório de scripts do Python está no PATH
2. Usar os scripts universais de desinstalação
3. Realizar a desinstalação manual com pip

### Permissão negada (Linux/macOS)

Se encontrar erros de permissão:

```bash
# Torne o script executável
chmod +x quick-uninstall.sh

# Use sudo para desinstalar globalmente (se necessário)
sudo pip uninstall -y synapstor
```

### Erro de Arquivo em Uso (Windows)

Se um arquivo estiver bloqueado:

1. Feche qualquer aplicativo que possa estar usando o Synapstor
2. Reinicie o terminal/prompt de comando
3. Tente novamente a desinstalação

## Conclusão

O Synapstor fornece múltiplas opções de desinstalação para garantir flexibilidade em diferentes ambientes e casos de uso. A maioria dos usuários terá sucesso usando um dos comandos simples (`synapstor-remove` ou `uninstall-synapstor`), mas opções mais avançadas estão disponíveis para casos especiais. 