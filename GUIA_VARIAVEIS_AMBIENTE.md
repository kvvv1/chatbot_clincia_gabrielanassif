# 🔧 Guia Completo - Configuração de Variáveis de Ambiente

Este guia te ajudará a obter todas as informações necessárias para configurar as variáveis de ambiente do chatbot.

## 📋 Variáveis Obrigatórias

### 🔵 SUPABASE

**SUPABASE_URL**
- Acesse: https://supabase.com
- Faça login ou crie uma conta
- Crie um novo projeto
- Vá em **Settings > API**
- Copie a **Project URL** (formato: `https://seu-projeto.supabase.co`)

**SUPABASE_ANON_KEY**
- Na mesma página **Settings > API**
- Copie a **anon public** key
- Formato: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**SUPABASE_SERVICE_ROLE_KEY**
- Na mesma página **Settings > API**
- Copie a **service_role** key (chave secreta)
- ⚠️ **IMPORTANTE**: Esta chave tem acesso total ao banco

### 🟢 Z-API (WhatsApp)

**ZAPI_TOKEN**
- Acesse: https://z-api.io
- Faça login ou crie uma conta
- Vá em **Configurações > Tokens**
- Crie um novo token ou copie um existente
- Formato: `seu-token-aqui`

**WEBHOOK_URL**
- Esta será a URL do seu app no Vercel
- Formato: `https://seu-app.vercel.app/webhook`
- ⚠️ **IMPORTANTE**: Configure após fazer o deploy no Vercel

### 🟡 GESTÃODS (Opcional)

**GESTAODS_URL**
- URL padrão: `https://api.gestaods.com.br`
- Se sua clínica usa outro domínio, ajuste conforme necessário

**GESTAODS_TOKEN**
- Solicite ao administrador do sistema GestãoDS
- Ou entre em contato com o suporte do GestãoDS

**GESTAODS_CLINIC_ID**
- ID da sua clínica no sistema GestãoDS
- Solicite ao administrador do sistema

## ⚙️ Variáveis Opcionais (com valores padrão)

### Configurações Gerais
- **APP_NAME**: Nome da aplicação (padrão: "Chatbot Clínica")
- **DEBUG**: Modo debug (padrão: "false")
- **LOG_LEVEL**: Nível de log (padrão: "INFO")

### WebSocket
- **WEBSOCKET_URL**: URL do WebSocket (padrão: "wss://localhost:8000/ws")

### CORS
- **CORS_ORIGINS**: Origins permitidos (padrão: "http://localhost:3000,https://seu-app.vercel.app")

### Informações da Clínica
- **CLINIC_NAME**: Nome da clínica (padrão: "Clínica Exemplo")
- **CLINIC_PHONE**: Telefone da clínica (padrão: "+5531999999999")
- **CLINIC_ADDRESS**: Endereço da clínica (padrão: "Rua Exemplo, 123 - Cidade")

### Configurações Avançadas
- **MAX_RETRIES**: Máximo de tentativas para APIs (padrão: "3")
- **REQUEST_TIMEOUT**: Timeout das requisições em segundos (padrão: "30")
- **VERCEL**: Executando no Vercel (padrão: "true")

## 🚀 Como Configurar

### Opção 1: Script Interativo (Recomendado)
```bash
python configurar_variaveis_ambiente.py
```

### Opção 2: Manual
1. Crie um arquivo `.env` na raiz do projeto
2. Adicione as variáveis no formato:
```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-chave-anonima
SUPABASE_SERVICE_ROLE_KEY=sua-chave-servico
ZAPI_TOKEN=seu-token-zapi
WEBHOOK_URL=https://seu-app.vercel.app/webhook
# ... outras variáveis
```

## 📝 Exemplo de Arquivo .env Completo

```env
# Configurações do Chatbot
# Gerado automaticamente pelo configurador

# SUPABASE
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Z-API (WhatsApp)
ZAPI_TOKEN=seu-token-zapi
WEBHOOK_URL=https://seu-app.vercel.app/webhook

# GESTÃODS
GESTAODS_URL=https://api.gestaods.com.br
GESTAODS_TOKEN=seu-token-gestaods
GESTAODS_CLINIC_ID=12345

# CONFIGURAÇÕES GERAIS
APP_NAME=Chatbot Clínica
DEBUG=false
LOG_LEVEL=INFO

# WEBSOCKET
WEBSOCKET_URL=wss://seu-app.vercel.app/ws

# CORS
CORS_ORIGINS=http://localhost:3000,https://seu-app.vercel.app

# INFORMAÇÕES DA CLÍNICA
CLINIC_NAME=Clínica Exemplo
CLINIC_PHONE=+5531999999999
CLINIC_ADDRESS=Rua Exemplo, 123 - Cidade

# CONFIGURAÇÕES AVANÇADAS
MAX_RETRIES=3
REQUEST_TIMEOUT=30
VERCEL=true
```

## 🔍 Verificação das Configurações

Após configurar as variáveis, execute:

```bash
python setup_all_connections.py
```

Este script irá testar todas as conexões e informar se está tudo funcionando.

## ⚠️ Dicas Importantes

1. **Segurança**: Nunca compartilhe as chaves do Supabase ou tokens
2. **Webhook URL**: Configure após fazer o deploy no Vercel
3. **Backup**: Mantenha backup das suas configurações
4. **Teste**: Sempre teste as conexões antes do deploy
5. **Ambiente**: Use variáveis diferentes para desenvolvimento e produção

## 🆘 Suporte

Se precisar de ajuda:
1. Verifique se todas as URLs estão corretas
2. Confirme se os tokens estão válidos
3. Teste as conexões individualmente
4. Consulte a documentação dos serviços

## 📞 Contatos Úteis

- **Supabase**: https://supabase.com/docs
- **Z-API**: https://z-api.io/docs
- **GestãoDS**: Suporte do seu sistema
- **Vercel**: https://vercel.com/docs 