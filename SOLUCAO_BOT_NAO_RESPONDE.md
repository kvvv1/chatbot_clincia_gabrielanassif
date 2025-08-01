# 🚨 SOLUÇÃO: BOT NÃO RESPONDE ÀS MENSAGENS

## 🔍 **DIAGNÓSTICO DO PROBLEMA**

O bot não está respondendo porque:
1. ❌ **Variáveis de ambiente não configuradas no Vercel**
2. ❌ **Webhook não configurado no Z-API**
3. ❌ **Credenciais Z-API não estão sendo lidas pela aplicação**

## 🔧 **SOLUÇÃO PASSO A PASSO**

### **PASSO 1: Configurar Variáveis no Vercel**

1. **Acesse o painel do Vercel:**
   - https://vercel.com/dashboard
   - Vá para seu projeto: `chatbot-clincia`
   - Clique em `Settings` → `Environment Variables`

2. **Adicione as seguintes variáveis:**

#### **Z-API (OBRIGATÓRIO)**
```
ZAPI_INSTANCE_ID = 3E4F7360B552F0C2DBCB9E6774402775
ZAPI_TOKEN = 17829E98BB59E9ADD55BBBA9
ZAPI_CLIENT_TOKEN = Fb79b25350a784c8e83d4a25213955ab5S
ZAPI_BASE_URL = https://api.z-api.io
```

#### **Supabase (OBRIGATÓRIO)**
```
SUPABASE_URL = https://feqylqrphdpeeusdyeyw.supabase.co
SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NzQwOTksImV4cCI6MjA2OTQ1MDA5OX0.cavDpXtpWn28D_FN6prGFjXATj8DdaUPdG7Rrd-m_kI
```

#### **GestãoDS (JÁ CONFIGURADO)**
```
GESTAODS_API_URL = https://apidev.gestaods.com.br
GESTAODS_TOKEN = 733a8e19a94b65d58390da380ac946b6d603a535
```

#### **Aplicação**
```
ENVIRONMENT = production
DEBUG = false
WEBSOCKET_ENABLED = false
CORS_ORIGINS = *
```

3. **Clique em `Save`**
4. **Faça um novo deploy** (clique em `Deployments` → `Redeploy`)

### **PASSO 2: Configurar Webhook no Z-API**

1. **Acesse o painel Z-API:**
   - https://app.z-api.io/
   - Faça login na sua conta
   - Vá para "Instâncias"
   - Clique na instância: `3E4F7360B552F0C2DBCB9E6774402775`

2. **Configure o Webhook:**
   - Vá para a aba "Webhook" ou "Configurações"
   - **URL do Webhook:** `https://chatbot-clincia.vercel.app/webhook`
   - **Eventos:** Marque todos os eventos (message, status, connected)
   - **Salve** as configurações

### **PASSO 3: Verificar Configuração**

Execute o script de verificação:

```bash
python configurar_webhook_zapi_final.py
```

### **PASSO 4: Testar o Sistema**

1. **Envie uma mensagem** para o número cadastrado no Z-API
2. **Verifique os logs** no Vercel:
   - https://vercel.com/dashboard
   - Seu projeto → `Functions` → `webhook` → `View Function Logs`

## 🧪 **TESTES AUTOMÁTICOS**

### **Teste 1: Verificar Vercel**
```bash
python test_vercel_config.py
```

### **Teste 2: Verificar Webhook**
```bash
python verificar_webhook_config.py
```

### **Teste 3: Configurar Webhook**
```bash
python configurar_webhook_zapi_final.py
```

## 🔍 **VERIFICAÇÃO MANUAL**

### **1. Testar Endpoints Vercel**
```bash
# Health check
curl https://chatbot-clincia.vercel.app/health

# Webhook
curl https://chatbot-clincia.vercel.app/webhook
```

### **2. Verificar Z-API**
- Acesse: https://app.z-api.io/
- Verifique se a instância está ativa
- Verifique se o WhatsApp está conectado

### **3. Verificar Logs**
- Vercel Dashboard → Functions → webhook → Logs
- Procure por erros ou mensagens de debug

## 🚨 **PROBLEMAS COMUNS E SOLUÇÕES**

### **Problema 1: "Instance not found"**
**Solução:** Verifique se o `ZAPI_INSTANCE_ID` está correto

### **Problema 2: "Webhook not configured"**
**Solução:** Configure o webhook no painel Z-API

### **Problema 3: "Variables not found"**
**Solução:** Configure as variáveis no Vercel

### **Problema 4: "WhatsApp not connected"**
**Solução:** Conecte o WhatsApp no painel Z-API

## 📱 **TESTE FINAL**

Após configurar tudo:

1. **Envie "oi"** para o número do WhatsApp
2. **O bot deve responder** com o menu principal
3. **Verifique os logs** no Vercel para confirmar

## 🆘 **SE AINDA NÃO FUNCIONAR**

1. **Verifique os logs** no Vercel
2. **Teste os endpoints** manualmente
3. **Confirme as credenciais** Z-API
4. **Verifique se o webhook** está configurado corretamente

## 📞 **SUPORTE**

- **Vercel:** https://vercel.com/support
- **Z-API:** https://z-api.io/support
- **Logs:** https://vercel.com/dashboard → Functions → Logs

---

**🎯 RESULTADO ESPERADO:**
Após seguir todos os passos, o bot deve responder automaticamente às mensagens enviadas para o número cadastrado no Z-API. 