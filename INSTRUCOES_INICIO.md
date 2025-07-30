# 🚀 Instruções para Iniciar o Chatbot

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 16+
- npm ou yarn
- Git

## 🛠️ Configuração Inicial

### 1. Configurar o Backend (Python/FastAPI)

```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Instalar dependências (já feito)
pip install -r requirements.txt

# Copiar arquivo de configuração
copy env.example .env
```

### 2. Configurar o Frontend (React)

```bash
# Navegar para o diretório do frontend
cd dashboard-frontend

# Instalar dependências (já feito)
npm install
```

## 🚀 Iniciar os Serviços

### Opção 1: Script Automático (Recomendado)

Execute um dos scripts abaixo:

**Windows (PowerShell):**
```powershell
.\start_services.ps1
```

**Windows (CMD):**
```cmd
start_services.bat
```

### Opção 2: Manual

**Terminal 1 - Backend:**
```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Iniciar servidor FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
# Navegar para o frontend
cd dashboard-frontend

# Iniciar servidor React
npm start
```

## 🌐 URLs dos Serviços

- **Backend API:** http://localhost:8000
- **Frontend Dashboard:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔧 Configuração do Ambiente

Edite o arquivo `.env` com suas credenciais:

```env
# Z-API Credentials
ZAPI_INSTANCE_ID=seu_instance_id
ZAPI_TOKEN=seu_token
ZAPI_CLIENT_TOKEN=seu_client_token

# GestãoDS API
GESTAODS_API_URL=https://apidev.gestaods.com.br
GESTAODS_TOKEN=seu_token_gestaods

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_clinica

# App Settings
APP_HOST=0.0.0.0
APP_PORT=8000
ENVIRONMENT=development
DEBUG=True

# Clinic Info
CLINIC_NAME=Clínica Gabriela Nassif
CLINIC_PHONE=5531999999999
REMINDER_HOUR=18
REMINDER_MINUTE=0
```

## 🐳 Usando Docker (Alternativa)

Se preferir usar Docker:

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## 🧪 Executar Testes

### Backend Tests:
```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Executar testes
pytest
```

### Frontend Tests:
```bash
cd dashboard-frontend
npm test
```

## 📝 Estrutura do Projeto

```
chatbot/
├── app/                    # Backend FastAPI
│   ├── handlers/          # Handlers das rotas
│   ├── models/            # Modelos de dados
│   ├── services/          # Lógica de negócio
│   └── utils/             # Utilitários
├── dashboard-frontend/     # Frontend React
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── hooks/         # Custom hooks
│   │   └── services/      # Serviços de API
└── tests/                 # Testes do backend
```

## 🔍 Troubleshooting

### Problemas Comuns:

1. **Porta 8000 em uso:**
   ```bash
   # Verificar processos na porta
   netstat -ano | findstr :8000
   # Matar processo se necessário
   taskkill /PID <PID> /F
   ```

2. **Porta 3000 em uso:**
   ```bash
   # Verificar processos na porta
   netstat -ano | findstr :3000
   # Matar processo se necessário
   taskkill /PID <PID> /F
   ```

3. **Erro de dependências Python:**
   ```bash
   # Reinstalar dependências
   pip install -r requirements.txt --force-reinstall
   ```

4. **Erro de dependências Node.js:**
   ```bash
   cd dashboard-frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

## 📞 Suporte

Se encontrar problemas, verifique:
1. Logs do backend no terminal
2. Logs do frontend no terminal
3. Console do navegador (F12)
4. Network tab do navegador para requisições 