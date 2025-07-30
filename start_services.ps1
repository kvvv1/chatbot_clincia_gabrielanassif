Write-Host "Iniciando o Chatbot - Backend e Frontend" -ForegroundColor Green
Write-Host ""

Write-Host "1. Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "2. Iniciando o backend na porta 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

Write-Host ""
Write-Host "3. Aguardando 3 segundos para o backend inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "4. Iniciando o frontend na porta 3000..." -ForegroundColor Yellow
Set-Location dashboard-frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start" -WindowStyle Normal

Write-Host ""
Write-Host "Serviços iniciados!" -ForegroundColor Green
Write-Host "- Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "- Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "- API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 