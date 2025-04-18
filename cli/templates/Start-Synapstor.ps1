#!/usr/bin/env pwsh

Write-Host "Starting Synapstor server..." -ForegroundColor Cyan
synapstor-server
Write-Host "Press any key to continue..." -NoNewLine
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""
