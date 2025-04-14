#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Inicia o servidor MCP Qdrant com suporte a arquivo .env
.DESCRIPTION
    Este script facilita a inicialização do servidor MCP Qdrant
    carregando automaticamente as configurações de um arquivo .env
.PARAMETER Transport
    Protocolo de transporte (stdio ou sse, padrão: sse)
.PARAMETER EnvFile
    Caminho para o arquivo .env (padrão: .env na pasta atual)
.PARAMETER CreateEnv
    Cria um arquivo .env de exemplo se não existir
.EXAMPLE
    .\Start-Server.ps1
.EXAMPLE
    .\Start-Server.ps1 -Transport stdio
.EXAMPLE
    .\Start-Server.ps1 -CreateEnv
#>

param (
    [ValidateSet("stdio", "sse")]
    [string]$Transport = "sse",
    
    [string]$EnvFile = ".env",
    
    [switch]$CreateEnv
)

# Prepara os argumentos
$args = @("scripts\start_server.py", "--transport", $Transport)

if ($EnvFile -ne ".env") {
    $args += "--env-file"
    $args += $EnvFile
}

if ($CreateEnv) {
    $args += "--create-env"
}

Write-Host "Iniciando servidor MCP Qdrant..."
# Executa o script Python com os argumentos fornecidos
& python $args

# Aguarda entrada do usuário antes de fechar
if (-not $?) {
    Write-Host "Erro ao iniciar o servidor" -ForegroundColor Red
}
Write-Host "Pressione qualquer tecla para continuar..." -NoNewLine
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host "" 