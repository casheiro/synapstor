# Script simples para desinstalar o Synapstor (Windows PowerShell)

Write-Host "Desinstalando Synapstor..." -ForegroundColor Cyan
pip uninstall -y synapstor

Write-Host "Synapstor removido com sucesso!" -ForegroundColor Green
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 