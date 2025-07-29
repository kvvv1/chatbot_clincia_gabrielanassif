@echo off
echo 🤖 Iniciando ambiente de desenvolvimento...

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.11+
    pause
    exit /b 1
)

REM Verificar se pip está instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não encontrado
    pause
    exit /b 1
)

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo 📚 Instalando dependências...
pip install -r requirements.txt

REM Verificar se arquivo .env existe
if not exist ".env" (
    echo ⚠️  Arquivo .env não encontrado!
    echo 📝 Copiando arquivo de exemplo...
    copy env.example .env
    echo 🔧 Configure as variáveis de ambiente no arquivo .env
    echo 📖 Veja o README.md para instruções de configuração
)

echo ✅ Ambiente configurado!
echo 🚀 Para iniciar a aplicação:
echo    python run.py
echo    ou
echo    uvicorn app.main:app --reload

pause 