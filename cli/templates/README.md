# 🚀 Templates de Inicialização do Synapstor | Synapstor Startup Templates

## Índice | Table of Contents
- [Português](#português)
- [English](#english)

---

<a name="português"></a>
# 🚀 Templates de Inicialização do Synapstor (Português)

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

# Matrix Embedding Framework (MEF)
export MEF_ENABLED="true"
export MEF_ENFORCE_STRUCTURE="true"

synapstor-server
```

### Usar com synapstor-ctl

Modifique os scripts para usar a interface centralizada `synapstor-ctl`:

```powershell
#!/usr/bin/env pwsh

Write-Host "Iniciando servidor Synapstor via synapstor-ctl..." -ForegroundColor Cyan
synapstor-ctl start
Write-Host "Pressione qualquer tecla para continuar..." -NoNewLine
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""
```

### Configurar Matrix Embedding Framework (MEF)

Para ativar o suporte ao MEF nos scripts de inicialização:

```batch
@echo off
echo Iniciando servidor Synapstor com suporte MEF...
set MEF_ENABLED=true
set MEF_ENFORCE_STRUCTURE=true
synapstor-server
pause
```

```powershell
#!/usr/bin/env pwsh

Write-Host "Iniciando servidor Synapstor com MEF..." -ForegroundColor Green
$env:MEF_ENABLED="true"
$env:MEF_ENFORCE_STRUCTURE="true"
synapstor-server
```

## 📝 Notas

- Estes scripts assumem que o Synapstor já está instalado e disponível no PATH do sistema
- Para servidores de produção, considere usar sistemas de gerenciamento de processos como systemd (Linux) ou serviços do Windows em vez destes scripts
- Você pode combinar estes scripts com arquivos `.env` para configurações mais complexas
- O Matrix Embedding Framework (MEF) pode ser ativado definindo `MEF_ENABLED=true` nas variáveis de ambiente

---

<a name="english"></a>
# 🚀 Synapstor Startup Templates (English)

This directory contains startup scripts for Synapstor on different platforms, making it easier to run the server without typing commands in the terminal.

## 📋 Overview

The startup templates are pre-configured scripts that simplify the process of starting the Synapstor server. They are especially useful for:

- Users who prefer to start the server with a double-click instead of using the terminal
- Creating shortcuts on the desktop or taskbar
- Distributing default configurations to team members
- Integrating Synapstor into automated workflows

## 🗂️ Available Scripts

### 1. `start-synapstor.bat`

**Platform**: Windows (Command Prompt)

This basic batch script starts the Synapstor server on Windows systems through the Command Prompt.

```batch
@echo off
echo Starting Synapstor server...
synapstor-server
pause
```

### 2. `Start-Synapstor.ps1`

**Platform**: Windows (PowerShell)

A more advanced version for Windows that uses PowerShell, with better visual formatting and feedback.

```powershell
#!/usr/bin/env pwsh

Write-Host "Starting Synapstor server..." -ForegroundColor Cyan
synapstor-server
Write-Host "Press any key to continue..." -NoNewLine
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""
```

### 3. `start-synapstor.sh`

**Platform**: Linux/macOS (Bash)

Shell script for Unix-based systems (Linux and macOS).

```bash
#!/bin/bash

echo "Starting Synapstor server..."
synapstor-server
```

## 🔧 Usage

### Automatic Installation

During Synapstor configuration via `synapstor-ctl configure`, you can choose to install a startup script appropriate for your system. The system will identify your platform and copy the correct script to an easily accessible location.

### Manual Installation

To use these templates manually:

1. **Windows (Batch)**:
   - Copy `start-synapstor.bat` to any location (e.g., Desktop)
   - Double-click to run

2. **Windows (PowerShell)**:
   - Copy `Start-Synapstor.ps1` to any location
   - Right-click on the file and select "Run with PowerShell"
   - Important: You may need to adjust the execution policy with: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

3. **Linux/macOS**:
   - Copy `start-synapstor.sh` to a location of your choice
   - Make it executable: `chmod +x start-synapstor.sh`
   - Run with: `./start-synapstor.sh`

## ✨ Customization

You can customize these scripts to meet your specific needs:

### Adding Transport Parameters

To configure the server with SSE transport (recommended for Cursor):

```batch
@echo off
echo Starting Synapstor server with SSE transport...
synapstor-server --transport sse
pause
```

### Adding Environment Variables

Configure environment variables directly in the script:

```bash
#!/bin/bash

echo "Starting Synapstor server with custom settings..."
export QDRANT_URL="http://localhost:6333"
export COLLECTION_NAME="my-project"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Matrix Embedding Framework (MEF)
export MEF_ENABLED="true"
export MEF_ENFORCE_STRUCTURE="true"

synapstor-server
```

### Using with synapstor-ctl

Modify the scripts to use the centralized `synapstor-ctl` interface:

```powershell
#!/usr/bin/env pwsh

Write-Host "Starting Synapstor server via synapstor-ctl..." -ForegroundColor Cyan
synapstor-ctl start
Write-Host "Press any key to continue..." -NoNewLine
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""
```

### Configure Matrix Embedding Framework (MEF)

To enable MEF support in startup scripts:

```batch
@echo off
echo Starting Synapstor server with MEF support...
set MEF_ENABLED=true
set MEF_ENFORCE_STRUCTURE=true
synapstor-server
pause
```

```powershell
#!/usr/bin/env pwsh

Write-Host "Starting Synapstor server with MEF..." -ForegroundColor Green
$env:MEF_ENABLED="true"
$env:MEF_ENFORCE_STRUCTURE="true"
synapstor-server
```

## 📝 Notes

- These scripts assume that Synapstor is already installed and available in the system PATH
- For production servers, consider using process management systems like systemd (Linux) or Windows services instead of these scripts
- You can combine these scripts with `.env` files for more complex configurations
- Matrix Embedding Framework (MEF) can be enabled by setting `MEF_ENABLED=true` in environment variables
