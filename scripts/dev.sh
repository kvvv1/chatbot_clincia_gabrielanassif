#!/bin/bash

echo "🤖 Iniciando ambiente de desenvolvimento..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.11+"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado"
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Copiando arquivo de exemplo..."
    cp env.example .env
    echo "🔧 Configure as variáveis de ambiente no arquivo .env"
    echo "📖 Veja o README.md para instruções de configuração"
fi

# Verificar se PostgreSQL está rodando
if ! pg_isready -q; then
    echo "⚠️  PostgreSQL não está rodando"
    echo "💡 Inicie o PostgreSQL ou use Docker:"
    echo "   docker-compose up -d db"
fi

echo "✅ Ambiente configurado!"
echo "🚀 Para iniciar a aplicação:"
echo "   python run.py"
echo "   ou"
echo "   uvicorn app.main:app --reload" 