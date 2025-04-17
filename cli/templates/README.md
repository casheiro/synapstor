# 🚀 Templates de Inicialização do Synapstor

Este diretório contém scripts de inicialização para o Synapstor em diferentes plataformas, facilitando a execução do servidor sem a necessidade de digitar comandos no terminal.

## 📋 Visão Geral

Os templates de inicialização são scripts pré-configurados que simplificam o processo de iniciar o servidor Synapstor. Eles são especialmente úteis para:

- Usuários que preferem iniciar o servidor com um duplo clique em vez de usar o terminal
- Criar atalhos no desktop ou na barra de tarefas
- Distribuir configurações padrão para membros da equipe
- Integrar o Synapstor em fluxos de trabalho automatizados

## 🗂️ Scripts Disponíveis

### 1. `start-synapstor.bat`

**Plataforma**: Windows (Prompt de Comando)

Este script batch básico inicia o servidor Synapstor em sistemas Windows através do Prompt de Comando.

```batch
@echo off
echo Iniciando servidor Synapstor...
synapstor-server
pause
```

### 2. `Start-Synapstor.ps1`

**Plataforma**: Windows (PowerShell)

Uma versão mais avançada para Windows que usa PowerShell, com melhor formatação visual e feedback.

```powershell
#!/usr/bin/env pwsh

Write-Host "Iniciando servidor Synapstor..." -ForegroundColor Cyan
synapstor-server
Write-Host "Pressione qualquer tecla para continuar..." -NoNewLine
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""
```

### 3. `start-synapstor.sh`

**Plataforma**: Linux/macOS (Bash)

Script shell para sistemas baseados em Unix (Linux e macOS).

```bash
#!/bin/bash

echo "Iniciando servidor Synapstor..."
synapstor-server
```

## 🔧 Uso

### Instalação Automática

Durante a configuração do Synapstor via `synapstor-ctl configure`, você pode optar por instalar um script de inicialização apropriado para o seu sistema. O sistema identificará sua plataforma e copiará o script correto para um local de fácil acesso.

### Instalação Manual

Para usar estes templates manualmente:

1. **Windows (Batch)**:
   - Copie `start-synapstor.bat` para qualquer local (ex: Desktop)
   - Dê um duplo clique para executar

2. **Windows (PowerShell)**:
   - Copie `Start-Synapstor.ps1` para qualquer local
   - Clique com o botão direito no arquivo e selecione "Executar com PowerShell"
   - Importante: Pode ser necessário ajustar a política de execução com: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

3. **Linux/macOS**:
   - Copie `start-synapstor.sh` para um local de sua escolha
   - Torne-o executável: `chmod +x start-synapstor.sh`
   - Execute com: `./start-synapstor.sh`

## ✨ Personalização

Você pode personalizar estes scripts para atender às suas necessidades específicas:

### Adicionar Parâmetros de Transporte

Para configurar o servidor com transporte SSE (recomendado para Cursor):

```batch
@echo off
echo Iniciando servidor Synapstor com transporte SSE...
synapstor-server --transport sse
pause
```

### Adicionar Variáveis de Ambiente

Configure as variáveis de ambiente diretamente no script:

```bash
#!/bin/bash

echo "Iniciando servidor Synapstor com configurações personalizadas..."
export QDRANT_URL="http://localhost:6333"
export COLLECTION_NAME="meu-projeto"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
synapstor-server
```

### Usar com synapstor-ctl

Modifique os scripts para usar a interface centralizada `synapstor-ctl`:

```powershell
#!/usr/bin/env pwsh

Write-Host "Iniciando servidor Synapstor via synapstor-ctl..." -ForegroundColor Cyan
synapstor-ctl server
Write-Host "Pressione qualquer tecla para continuar..." -NoNewLine
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""
```

## 📝 Notas

- Estes scripts assumem que o Synapstor já está instalado e disponível no PATH do sistema
- Para servidores de produção, considere usar sistemas de gerenciamento de processos como systemd (Linux) ou serviços do Windows em vez destes scripts
- Você pode combinar estes scripts com arquivos `.env` para configurações mais complexas
