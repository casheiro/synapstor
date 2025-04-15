@echo off
echo Desinstalando Synapstor...

:: Tenta encontrar o Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python -m pip uninstall -y synapstor
) else (
    :: Tenta com python3
    where python3 >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        python3 -m pip uninstall -y synapstor
    ) else (
        :: Tenta usar o pip diretamente
        where pip >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            pip uninstall -y synapstor
        ) else (
            echo ERRO: Python ou pip nao encontrado.
            echo Por favor, execute: pip uninstall -y synapstor
        )
    )
)

echo.
echo Desinstalacao concluida!
pause 