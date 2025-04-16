#!/usr/bin/env pwsh

Write-Host "Iniciando servidor Synapstor..." -ForegroundColor Cyan
synapstor-server
Write-Host "Pressione qualquer tecla para continuar..." -NoNewLine
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host "" 