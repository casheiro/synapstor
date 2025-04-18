@echo off
:: Script para iniciar o servidor Synapstor com suporte bilíngue
:: Script to start the Synapstor server with bilingual support

:: Verificar localidade do sistema
:: Check system locale
for /f "tokens=3 delims= " %%G in ('systeminfo ^| find "System Locale"') do set LOCALE=%%G

:: Detectar idioma preferido
:: Detect preferred language
echo %LOCALE% | findstr /i "pt-br pt_br pt-pt pt_pt" > nul
if %errorlevel% equ 0 (
    echo Iniciando servidor Synapstor...
) else (
    echo Starting Synapstor server...
)

:: Iniciar o servidor
:: Start the server
synapstor-server
pause
