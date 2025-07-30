# 🚀 Instruções de Deploy - Chatbot Clínica

## 📋 Pré-requisitos

### 1. **Z-API (WhatsApp)**
- Criar conta em https://z-api.io
- Obter credenciais:
  - `ZAPI_INSTANCE_ID`
  - `ZAPI_TOKEN` 
  - `ZAPI_CLIENT_TOKEN`

### 2. **GestãoDS** ✅ **CONFIGURADO**
- ✅ Token já configurado: `733a8e19a94b65d58390da380ac946b6d603a535`
- ✅ API URL configurada: `https://apidev.gestaods.com.br`
- ✅ Widget integrado e funcionando
- 📖 Documentação: https://apidev.gestaods.com.br/redoc

### 3. **Banco de Dados** ✅ **SUPABASE CONFIGURADO**
- ✅ **Supabase**: Configuração completa implementada
  - Criar projeto em https://supabase.com
  - Seguir guia em `SUPABASE_SETUP.md`
  - Obter `SUPABASE_URL`, `SUPABASE_ANON_KEY` e `SUPABASE_SERVICE_ROLE_KEY`
- **Opção B**: PostgreSQL
  - Usar serviço como Railway, PlanetScale, etc.

## 🔧 Deploy Backend (Vercel)

### 1. **Preparar repositório**
```bash
# Fazer commit das alterações
git add .
git commit -m "Configuração para deploy"
git push origin main
```

### 2. **Conectar ao Vercel**
1. Acessar https://vercel.com
2. Importar repositório do GitHub
3. Configurar:
   - **Framework Preset**: Other
   - **Build Command**: `pip install -r requirements-vercel.txt`
   - **Output Directory**: `app`
   - **Install Command**: `pip install -r requirements-vercel.txt`

### 3. **Configurar Variáveis de Ambiente**
No painel do Vercel, adicionar:

```env
# Z-API (OBRIGATÓRIO)
ZAPI_INSTANCE_ID=seu_instance_id_real
ZAPI_TOKEN=seu_token_real
ZAPI_CLIENT_TOKEN=seu_client_token_real

# GestãoDS (OBRIGATÓRIO - Token já configurado)
GESTAODS_API_URL=https://apidev.gestaods.com.br
GESTAODS_TOKEN=733a8e19a94b65d58390da380ac946b6d603a535

# Database (OBRIGATÓRIO)
DATABASE_URL=postgresql://user:password@host:5432/database_name

# Supabase (RECOMENDADO - Configurar seguindo SUPABASE_SETUP.md)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_anonima_aqui
SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role_aqui

# App Settings
ENVIRONMENT=production
DEBUG=False
WEBSOCKET_ENABLED=True
WEBSOCKET_MAX_CONNECTIONS=50

# CORS (OBRIGATÓRIO)
CORS_ORIGINS=https://seu-frontend.netlify.app
CORS_ALLOW_CREDENTIALS=True

# Clinic Info
CLINIC_NAME=Clínica Gabriela Nassif
CLINIC_PHONE=5531999999999
REMINDER_HOUR=18
REMINDER_MINUTE=0
```

### 4. **Deploy**
- Clicar em "Deploy"
- Aguardar build e deploy
- Anotar URL gerada (ex: `https://chatbot-clinica.vercel.app`)

## 🎨 Deploy Frontend (Netlify)

### 1. **Preparar frontend**
```bash
cd dashboard-frontend
npm install
npm run build
```

### 2. **Conectar ao Netlify**
1. Acessar https://netlify.com
2. Arrastar pasta `dashboard-frontend/build` para deploy
3. Ou conectar repositório GitHub

### 3. **Configurar Variáveis de Ambiente**
No painel do Netlify, adicionar:

```env
REACT_APP_API_URL=https://seu-backend.vercel.app
```

### 4. **Configurar domínio personalizado (opcional)**
- No painel do Netlify: Site settings > Domain management
- Adicionar domínio personalizado

## 🔗 Configuração Final

### 1. **Atualizar CORS no Backend**
No Vercel, atualizar `CORS_ORIGINS` com a URL do frontend:
```env
CORS_ORIGINS=https://seu-frontend.netlify.app
```

### 2. **Testar WebSocket**
- Acessar: `https://seu-backend.vercel.app/dashboard/ws-test`
- Deve retornar: `{"status": "ok", "message": "WebSocket endpoint está acessível"}`

### 3. **Testar API**
- Acessar: `https://seu-backend.vercel.app/health`
- Deve retornar status de saúde da aplicação

## 🧪 Testes Pós-Deploy

### 1. **Backend**
```bash
# Teste de saúde
curl https://seu-backend.vercel.app/health

# Teste WebSocket
curl https://seu-backend.vercel.app/dashboard/ws-test

# Teste dashboard
curl https://seu-backend.vercel.app/dashboard/test
```

### 2. **Frontend**
- Acessar URL do Netlify
- Verificar se carrega sem erros
- Testar conexão WebSocket
- Verificar se dados aparecem no dashboard

## 🚨 Troubleshooting

### Problemas Comuns:

1. **WebSocket não conecta**
   - Verificar se `WEBSOCKET_ENABLED=True`
   - Verificar CORS no frontend

2. **Erro de banco de dados**
   - Verificar `DATABASE_URL` ou `SUPABASE_URL`
   - Verificar se tabelas foram criadas

3. **Erro de Z-API**
   - Verificar credenciais do Z-API
   - Verificar se instância está ativa

4. **CORS errors**
   - Verificar `CORS_ORIGINS` no backend
   - Verificar `REACT_APP_API_URL` no frontend

## 📞 Suporte

- **Z-API**: https://z-api.io/support
- **GestãoDS**: Contato direto com a empresa
- **Supabase**: https://supabase.com/docs/support
- **Vercel**: https://vercel.com/support
- **Netlify**: https://netlify.com/support 