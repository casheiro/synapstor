#!/usr/bin/env pwsh

# Script para iniciar o servidor Synapstor com suporte bilíngue
# Script to start the Synapstor server with bilingual support

# Verificar a cultura atual do PowerShell
# Check current PowerShell culture
$CurrentCulture = (Get-Culture).Name

# Detectar idioma preferido
# Detect preferred language
if ($CurrentCulture -like "*pt*") {
    Write-Host "Iniciando servidor Synapstor..." -ForegroundColor Cyan
    $ContinueMessage = "Pressione qualquer tecla para continuar..."
} else {
    Write-Host "Starting Synapstor server..." -ForegroundColor Cyan
    $ContinueMessage = "Press any key to continue..."
}

# Iniciar o servidor
# Start the server
synapstor-server

# Pausa ao final da execução
# Pause at the end of execution
Write-Host $ContinueMessage -NoNewLine
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""
