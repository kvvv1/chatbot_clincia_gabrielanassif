@echo off
echo.
echo 🚀 SUBINDO APLICACAO DO CHATBOT
echo ================================
echo.

cd /d "%~dp0"

echo 📍 Diretorio atual: %CD%
echo.

echo 🔧 Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado!
    echo 💡 Instale Python 3.8+ e tente novamente
    pause
    exit /b 1
)

echo.
echo 📦 Instalando dependencias...
pip install -r requirements.txt

echo.
echo 🚀 Iniciando aplicacao...
echo ✅ Aplicacao estara disponivel em: http://localhost:8000
echo ✅ Webhook endpoint: http://localhost:8000/webhook
echo ✅ Dashboard: http://localhost:8000/dashboard
echo.
echo 💡 Para parar: Ctrl+C
echo 🔄 Deixe esta janela aberta...
echo.

python run.py

pause