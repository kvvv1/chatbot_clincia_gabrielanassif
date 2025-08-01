# 🚀 Configuração Vercel - Passo a Passo

## 📋 Passo 1: Acessar o Dashboard do Vercel

1. Vá para [vercel.com/dashboard](https://vercel.com/dashboard)
2. Clique no seu projeto `chatbot-clinica`
3. Vá para **Settings** (Configurações)

## 🔧 Passo 2: Configurar Environment Variables

1. No menu lateral, clique em **Environment Variables**
2. Clique em **Add New** para adicionar cada variável

### Z-API Configuration
Adicione estas 4 variáveis:

| Nome | Valor |
|------|-------|
| `ZAPI_INSTANCE_ID` | `3E4F7360B552F0C2DBCB9E6774402775` |
| `ZAPI_TOKEN` | `0BDEFB65E4B5E5615697BCD6` |
| `ZAPI_CLIENT_TOKEN` | `Fb79b25350a784c8e83d4a25213955ab5S` |
| `ZAPI_BASE_URL` | `https://api.z-api.io` |

### Supabase Configuration
Adicione estas 3 variáveis:

| Nome | Valor |
|------|-------|
| `SUPABASE_URL` | `https://feqylqrphdpeeusdyeyw.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NzQwOTksImV4cCI6MjA2OTQ1MDA5OX0.cavDpXtpWn28D_FN6prGFjXATj8DdaUPdG7Rrd-m_kI` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzg3NDA5OSwiZXhwIjoyMDY5NDUwMDk5fQ.gEF_cKRzAtDklZuTueVX_1XzaFrGONzECBS4tt13uIc` |

### GestãoDS Configuration
Adicione estas 2 variáveis:

| Nome | Valor |
|------|-------|
| `GESTAODS_API_URL` | `https://apidev.gestaods.com.br` |
| `GESTAODS_TOKEN` | `733a8e19a94b65d58390da380ac946b6d603a535` |

### App Configuration
Adicione estas variáveis:

| Nome | Valor |
|------|-------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `CORS_ORIGINS` | `*` |
| `CORS_ALLOW_CREDENTIALS` | `true` |

### Clinic Information
Adicione estas variáveis:

| Nome | Valor |
|------|-------|
| `CLINIC_NAME` | `Clínica Gabriela Nassif` |
| `CLINIC_PHONE` | `5531999999999` |
| `REMINDER_HOUR` | `18` |
| `REMINDER_MINUTE` | `0` |

### WebSocket Configuration
Adicione estas variáveis:

| Nome | Valor |
|------|-------|
| `WEBSOCKET_ENABLED` | `true` |
| `WEBSOCKET_MAX_CONNECTIONS` | `50` |

## 🔄 Passo 3: Redeploy

1. Vá para a aba **Deployments**
2. Clique no botão **Redeploy** no último deployment
3. Aguarde o deploy completar

## ✅ Passo 4: Testar

Após o deploy, teste estes endpoints:

- `https://chatbot-clinica.vercel.app/health`
- `https://chatbot-clinica.vercel.app/test`
- `https://chatbot-clinica.vercel.app/dashboard/status`

## 🚨 Importante

- **Environment**: Selecione `Production` para todas as variáveis
- **Preview**: Selecione `Production` para todas as variáveis
- **Development**: Selecione `Production` para todas as variáveis

## 📞 Suporte

Se algo der errado, verifique:
1. Se todas as variáveis foram adicionadas corretamente
2. Se os valores estão exatamente como mostrado acima
3. Se o redeploy foi executado após adicionar as variáveis 