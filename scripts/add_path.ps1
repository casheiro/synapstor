# Script para adicionar o diretório de scripts do Python ao PATH do Windows
# Este script é executado durante a instalação do Synapstor

function Add-ToPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Directory
    )
    
    Write-Host "Adicionando comandos do Synapstor ao PATH..."
    
    # Verifica se o diretório existe
    if (-not (Test-Path $Directory)) {
        Write-Host "Erro: O diretório $Directory não existe." -ForegroundColor Red
        return $false
    }
    
    # Verifica se está executando como administrador
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if ($isAdmin) {
        Write-Host "Executando como administrador..." -ForegroundColor Cyan
        
        try {
            # Obtém o PATH do sistema
            $systemPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
            
            # Verifica se o diretório já está no PATH
            if ($systemPath -split ";" -contains $Directory) {
                Write-Host "O diretório já está no PATH do sistema." -ForegroundColor Green
                return $true
            }
            
            # Adiciona o diretório ao PATH do sistema
            $newPath = $systemPath + ";" + $Directory
            [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::Machine)
            
            Write-Host "Adicionado com sucesso ao PATH do sistema!" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "Erro ao modificar o PATH do sistema: $_" -ForegroundColor Red
            return $false
        }
    }
    else {
        Write-Host "Executando como usuário normal..." -ForegroundColor Yellow
        
        try {
            # Obtém o PATH do usuário
            $userPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
            
            # Verifica se o diretório já está no PATH
            if ($userPath -split ";" -contains $Directory) {
                Write-Host "O diretório já está no PATH do usuário." -ForegroundColor Green
                return $true
            }
            
            # Adiciona o diretório ao PATH do usuário
            $newPath = $userPath + ";" + $Directory
            [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
            
            Write-Host "Adicionado com sucesso ao PATH do usuário!" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "Erro ao modificar o PATH do usuário: $_" -ForegroundColor Red
            return $false
        }
    }
}

# Determina o diretório de scripts do Python
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScripts = (Get-Item (Join-Path $scriptPath "..\")).FullName

Write-Host "Diretório detectado: $pythonScripts" -ForegroundColor Cyan

# Adiciona ao PATH
$result = Add-ToPath -Directory $pythonScripts

if ($result) {
    Write-Host "`nIMPORTANTE: Para que as alterações tenham efeito, você precisa reiniciar o PowerShell ou o computador." -ForegroundColor Yellow
}

# Aguarda uma tecla para continuar
Write-Host "`nPressione qualquer tecla para continuar..." -NoNewline
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host "" 