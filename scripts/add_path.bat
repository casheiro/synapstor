@echo off
:: Script para adicionar o diretório de scripts do Python ao PATH do Windows
:: Este script é executado durante a instalação do Synapstor

echo Adicionando comandos do Synapstor ao PATH...

:: Determina o diretório de scripts do Python
set SCRIPT_PATH=%~dp0
for %%F in ("%SCRIPT_PATH%..") do set PYTHON_SCRIPTS=%%~fF

echo Detectado: %PYTHON_SCRIPTS%

:: Verifica se é administrador
net session >nul 2>&1
if %errorlevel% == 0 (
    echo Executando como administrador...
    
    :: Adiciona ao PATH do sistema (requer privilégios de administrador)
    setx PATH "%PATH%;%PYTHON_SCRIPTS%" /M
    
    if %errorlevel% == 0 (
        echo Adicionado com sucesso ao PATH do sistema!
    ) else (
        echo Falha ao adicionar ao PATH do sistema.
    )
) else (
    echo Executando como usuário normal...
    
    :: Adiciona ao PATH do usuário (não requer privilégios de administrador)
    setx PATH "%PATH%;%PYTHON_SCRIPTS%"
    
    if %errorlevel% == 0 (
        echo Adicionado com sucesso ao PATH do usuário!
    ) else (
        echo Falha ao adicionar ao PATH do usuário.
    )
)

echo.
echo IMPORTANTE: Para que as alterações tenham efeito, você precisa reiniciar o prompt de comando ou o computador.
echo.

:: Pausa para mostrar a mensagem
pause 