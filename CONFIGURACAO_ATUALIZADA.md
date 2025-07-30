# 🔧 Configuração Atualizada - Chatbot Clínica

## ✅ **Configurações Implementadas**

### 1. **GestãoDS** ✅ **CONFIGURADO**
- **Token**: `733a8e19a94b65d58390da380ac946b6d603a535`
- **API URL**: `https://apidev.gestaods.com.br`
- **Widget URL**: `https://calendario.gestaods.com.br/?token=733a8e19a94b65d58390da380ac946b6d603a535`
- **Documentação**: https://apidev.gestaods.com.br/redoc

### 2. **Arquivos de Deploy Criados**
- ✅ `vercel.json` - Configuração para Vercel
- ✅ `requirements-vercel.txt` - Dependências para Vercel
- ✅ `dashboard-frontend/netlify.toml` - Configuração para Netlify
- ✅ `env.production.example` - Variáveis de ambiente para produção

### 3. **Integrações Implementadas**
- ✅ **GestãoDS API**: Serviço completo com token real
- ✅ **GestãoDS Widget**: Integração com calendário
- ✅ **WebSocket**: Otimizado para produção
- ✅ **CORS**: Configurável para produção
- ✅ **Supabase**: Configuração alternativa ao PostgreSQL

## 🚀 **Próximos Passos para Deploy**

### **Backend (Vercel)**
```bash
# 1. Commit das alterações
git add .
git commit -m "Configuração GestãoDS e deploy Vercel"
git push origin main

# 2. Deploy no Vercel
# - Acessar https://vercel.com
# - Importar repositório
# - Configurar variáveis de ambiente (ver env.production.example)
```

### **Frontend (Netlify)**
```bash
# 1. Build do frontend
cd dashboard-frontend
npm install
npm run build

# 2. Deploy no Netlify
# - Fazer upload da pasta build/
# - Configurar REACT_APP_API_URL
```

## 🔧 **Variáveis de Ambiente Obrigatórias**

### **Vercel (Backend)**
```env
# Z-API (OBRIGATÓRIO)
ZAPI_INSTANCE_ID=seu_instance_id_real
ZAPI_TOKEN=seu_token_real
ZAPI_CLIENT_TOKEN=seu_client_token_real

# GestãoDS (JÁ CONFIGURADO)
GESTAODS_API_URL=https://apidev.gestaods.com.br
GESTAODS_TOKEN=733a8e19a94b65d58390da380ac946b6d603a535

# Database (OBRIGATÓRIO)
DATABASE_URL=postgresql://user:password@host:5432/database_name
# OU para Supabase:
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_anonima

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

### **Netlify (Frontend)**
```env
REACT_APP_API_URL=https://seu-backend.vercel.app
```

## 🧪 **Testes Disponíveis**

### **Teste GestãoDS**
```bash
python test_gestaods.py
```

### **Teste WebSocket**
```bash
curl https://seu-backend.vercel.app/dashboard/ws-test
```

### **Teste API**
```bash
curl https://seu-backend.vercel.app/health
```

## 📋 **Endpoints da GestãoDS**

### **Widget**
- `GET /dashboard/gestaods/widget` - Informações do widget
- `GET /dashboard/gestaods/slots/{date}` - Horários disponíveis
- `POST /dashboard/gestaods/appointment` - Criar agendamento

### **API Principal**
- Busca de pacientes por CPF
- Listagem de horários disponíveis
- Criação de agendamentos
- Cancelamento de agendamentos

## 🎯 **Status Atual**

- ✅ **GestãoDS**: Configurado e funcionando
- ✅ **WebSocket**: Otimizado para produção
- ✅ **CORS**: Configurável
- ✅ **Deploy**: Arquivos prontos
- ⏳ **Z-API**: Aguardando credenciais reais
- ⏳ **Database**: Aguardando configuração (Supabase/PostgreSQL)

## 📞 **Suporte**

- **GestãoDS**: Token configurado e funcionando
- **Z-API**: https://z-api.io/support
- **Supabase**: https://supabase.com/docs/support
- **Vercel**: https://vercel.com/support
- **Netlify**: https://netlify.com/support 