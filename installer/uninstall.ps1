# Script de desinstalação do Synapstor para Windows
# Autor: Synapstor Team
# Descrição: Remove o Synapstor do sistema, incluindo entradas do PATH, 
#            arquivos de configuração e pacote Python

# Executar como administrador para modificar variáveis de ambiente do sistema
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Este script requer permissões de administrador para remover corretamente o Synapstor."
    Write-Warning "Por favor, execute o PowerShell como administrador e tente novamente."
    exit
}

Write-Host "=== Desinstalador do Synapstor ===" -ForegroundColor Cyan
Write-Host "Este script irá remover o Synapstor do seu sistema." -ForegroundColor Yellow

# Confirmação do usuário
$confirmacao = Read-Host "Você tem certeza que deseja continuar? (S/N)"
if ($confirmacao -ne "S" -and $confirmacao -ne "s") {
    Write-Host "Desinstalação cancelada." -ForegroundColor Yellow
    exit
}

# Função para remover o Synapstor do PATH
function Remove-SynapstorFromPath {
    Write-Host "`nRemovendo Synapstor do PATH do sistema..." -ForegroundColor Cyan
    
    try {
        # Obter o PATH do usuário atual
        $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        
        if ($userPath -match "synapstor") {
            # Remover entradas relacionadas ao Synapstor do PATH
            $newPathEntries = $userPath.Split(';') | Where-Object { $_ -notmatch "synapstor" -and $_.Trim() -ne "" }
            $newPath = $newPathEntries -join ';'
            
            # Atualizar o PATH
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            Write-Host "PATH do usuário atualizado com sucesso." -ForegroundColor Green
        } else {
            Write-Host "Nenhuma entrada do Synapstor encontrada no PATH do usuário." -ForegroundColor Yellow
        }
        
        # Verificar também o PATH do sistema
        $systemPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        
        if ($systemPath -match "synapstor") {
            # Remover entradas relacionadas ao Synapstor do PATH do sistema
            $newSystemPathEntries = $systemPath.Split(';') | Where-Object { $_ -notmatch "synapstor" -and $_.Trim() -ne "" }
            $newSystemPath = $newSystemPathEntries -join ';'
            
            # Atualizar o PATH do sistema
            [Environment]::SetEnvironmentVariable("PATH", $newSystemPath, "Machine")
            Write-Host "PATH do sistema atualizado com sucesso." -ForegroundColor Green
        } else {
            Write-Host "Nenhuma entrada do Synapstor encontrada no PATH do sistema." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Erro ao atualizar o PATH: $_" -ForegroundColor Red
        Write-Host "Você precisará remover o Synapstor do PATH manualmente." -ForegroundColor Yellow
    }
}

# Função para remover arquivos de configuração
function Remove-ConfigFiles {
    Write-Host "`nRemovendo arquivos de configuração..." -ForegroundColor Cyan
    
    # Lista de diretórios que podem conter arquivos de configuração do Synapstor
    $configLocations = @(
        [System.IO.Path]::Combine($env:APPDATA, "Synapstor"),
        [System.IO.Path]::Combine($env:LOCALAPPDATA, "Synapstor")
    )
    
    foreach ($location in $configLocations) {
        if (Test-Path $location) {
            try {
                Remove-Item -Path $location -Recurse -Force
                Write-Host "Removido: $location" -ForegroundColor Green
            }
            catch {
                Write-Host "Erro ao remover $location: $_" -ForegroundColor Red
            }
        }
    }
    
    # Verificar arquivos de configuração do Cursor
    $cursorConfig = [System.IO.Path]::Combine($HOME, ".cursor", "mcp.json")
    if (Test-Path $cursorConfig) {
        Write-Host "Arquivo de configuração do Cursor detectado em: $cursorConfig" -ForegroundColor Yellow
        Write-Host "Recomendamos verificar manualmente este arquivo para remover configurações do Synapstor." -ForegroundColor Yellow
    }
}

# Função para desinstalar o pacote Python
function Uninstall-SynapstorPackage {
    Write-Host "`nDesinstalando o pacote Synapstor..." -ForegroundColor Cyan
    
    try {
        # Verificar se o Python está no PATH
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        
        if ($pythonCommand) {
            # Desinstalar via pip
            $process = Start-Process -FilePath "python" -ArgumentList "-m", "pip", "uninstall", "-y", "synapstor" -Wait -PassThru -NoNewWindow
            
            if ($process.ExitCode -eq 0) {
                Write-Host "Pacote Synapstor desinstalado com sucesso." -ForegroundColor Green
            } else {
                Write-Host "Erro ao desinstalar o pacote Synapstor. Código de saída: $($process.ExitCode)" -ForegroundColor Red
                Write-Host "Tente executar manualmente: pip uninstall -y synapstor" -ForegroundColor Yellow
            }
        } else {
            Write-Host "Python não encontrado no PATH. Você precisará desinstalar o pacote manualmente." -ForegroundColor Red
            Write-Host "Execute: pip uninstall -y synapstor" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Erro ao desinstalar o pacote: $_" -ForegroundColor Red
        Write-Host "Tente executar manualmente: pip uninstall -y synapstor" -ForegroundColor Yellow
    }
}

# Executar etapas de desinstalação
Remove-SynapstorFromPath
Remove-ConfigFiles
Uninstall-SynapstorPackage

Write-Host "`nDesinstalação concluída." -ForegroundColor Green
Write-Host "Obrigado por usar o Synapstor!" -ForegroundColor Cyan

# Aguardar antes de sair
Write-Host "`nPressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 