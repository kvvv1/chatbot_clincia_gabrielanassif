@echo off
echo Iniciando o Chatbot - Backend e Frontend
echo.

echo 1. Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo 2. Iniciando o backend na porta 8000...
start "Backend - FastAPI" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo 3. Aguardando 3 segundos para o backend inicializar...
timeout /t 3 /nobreak > nul

echo.
echo 4. Iniciando o frontend na porta 3000...
cd dashboard-frontend
start "Frontend - React" cmd /k "npm start"

echo.
echo Serviços iniciados!
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
echo - API Docs: http://localhost:8000/docs
echo.
echo Pressione qualquer tecla para sair...
pause > nul 