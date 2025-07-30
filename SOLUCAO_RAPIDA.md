# 🚀 Solução Rápida - Sem Vercel CLI

## ❌ Problema
O Vercel CLI não está instalado, mas você pode resolver o problema **manualmente** no dashboard do Vercel.

## ✅ Solução Manual (5 minutos)

### 1. Acesse o Dashboard do Vercel
- Vá para: https://vercel.com/dashboard
- Selecione seu projeto: `chatbot-clincia`

### 2. Configure as Variáveis de Ambiente
- Vá em: **Settings** → **Environment Variables**
- Clique em: **Add New**

### 3. Adicione as Variáveis (uma por uma)

#### Z-API (WhatsApp)
```
Nome: ZAPI_INSTANCE_ID
Valor: 3E4F7360B552F0C2DBCB9E6774402775
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: ZAPI_TOKEN
Valor: 17829E98BB59E9ADD55BBBA9
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: ZAPI_CLIENT_TOKEN
Valor: 17829E98BB59E9ADD55BBBA9
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: ZAPI_BASE_URL
Valor: https://api.z-api.io
Ambientes: ✅ Production ✅ Preview ✅ Development
```

#### Supabase (Database)
```
Nome: SUPABASE_URL
Valor: https://feqylqrphdpeeusdyeyw.supabase.co
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: SUPABASE_ANON_KEY
Valor: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NzQwOTksImV4cCI6MjA2OTQ1MDA5OX0.cavDpXtpWn28D_FN6prGFjXATj8DdaUPdG7Rrd-m_kI
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: SUPABASE_SERVICE_ROLE_KEY
Valor: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzg3NDA5OSwiZXhwIjoyMDY5NDUwMDk5fQ.gEF_cKRzAtDklZuTueVX_1XzaFrGONzECBS4tt13uIc
Ambientes: ✅ Production ✅ Preview ✅ Development
```

#### GestãoDS (Sistema)
```
Nome: GESTAODS_API_URL
Valor: https://apidev.gestaods.com.br
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: GESTAODS_TOKEN
Valor: 733a8e19a94b65d58390da380ac946b6d603a535
Ambientes: ✅ Production ✅ Preview ✅ Development
```

#### Clínica
```
Nome: CLINIC_NAME
Valor: Clínica Gabriela Nassif
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: CLINIC_PHONE
Valor: +553198600366
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: REMINDER_HOUR
Valor: 18
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: REMINDER_MINUTE
Valor: 0
Ambientes: ✅ Production ✅ Preview ✅ Development
```

#### App
```
Nome: ENVIRONMENT
Valor: production
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: DEBUG
Valor: false
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: CORS_ORIGINS
Valor: *
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: CORS_ALLOW_CREDENTIALS
Valor: true
Ambientes: ✅ Production ✅ Preview ✅ Development
```

#### WebSocket
```
Nome: WEBSOCKET_ENABLED
Valor: true
Ambientes: ✅ Production ✅ Preview ✅ Development

Nome: WEBSOCKET_MAX_CONNECTIONS
Valor: 50
Ambientes: ✅ Production ✅ Preview ✅ Development
```

### 4. Faça o Redeploy
- Vá em: **Deployments**
- Clique em: **Redeploy** no último deployment
- Aguarde o deploy terminar

### 5. Teste a Aplicação
- Acesse: https://chatbot-clincia.vercel.app/
- Deve retornar:
```json
{
  "status": "online",
  "service": "Chatbot Clínica",
  "version": "1.0.0",
  "environment": "vercel"
}
```

## 🎯 Resultado
✅ Aplicação funcionando em produção
✅ Sem erros de validação Pydantic
✅ Todas as funcionalidades operacionais

## 🚨 Se ainda houver problemas
1. Verifique se todas as variáveis estão marcadas para **Production**
2. Aguarde 2-3 minutos após configurar
3. Verifique os logs em: **Settings** → **Functions**

---
**Tempo estimado**: 5-10 minutos
**Dificuldade**: Fácil
**Resultado**: Aplicação funcionando 100% 