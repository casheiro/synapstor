@echo off
echo Desinstalador rapido do Synapstor
echo ==============================

:: Tenta encontrar o Python em diversos caminhos comuns
set PYTHON_PATHS=^
%LOCALAPPDATA%\Programs\Python\Python312\python.exe;^
%LOCALAPPDATA%\Programs\Python\Python311\python.exe;^
%LOCALAPPDATA%\Programs\Python\Python310\python.exe;^
%LOCALAPPDATA%\Programs\Python\Python39\python.exe;^
%ProgramFiles%\Python312\python.exe;^
%ProgramFiles%\Python311\python.exe;^
%ProgramFiles%\Python310\python.exe;^
%ProgramFiles%\Python39\python.exe;^
%USERPROFILE%\miniconda3\python.exe;^
%USERPROFILE%\Anaconda3\python.exe;^
C:\Python\python.exe

:: Procura Python no PATH
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Usando Python do PATH
    python -m pip uninstall -y synapstor
    goto :sucesso
)

:: Tenta cada caminho possível
for %%p in (%PYTHON_PATHS%) do (
    if exist "%%p" (
        echo Usando Python: %%p
        "%%p" -m pip uninstall -y synapstor
        goto :sucesso
    )
)

:: Tenta usar pip diretamente
where pip >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Usando pip do PATH
    pip uninstall -y synapstor
    goto :sucesso
)

echo Nao foi possivel encontrar Python ou pip no sistema.
echo Por favor, desinstale o Synapstor manualmente usando o comando:
echo pip uninstall -y synapstor
goto :fim

:sucesso
echo.
echo Synapstor desinstalado com sucesso!

:fim
echo.
pause 