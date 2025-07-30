# 🔧 Configuração de Variáveis de Ambiente no Vercel

## ❌ Problema Identificado

O erro nos logs do Vercel indica que **5 variáveis de ambiente obrigatórias estão faltando**:

- `zapi_instance_id`
- `zapi_token` 
- `zapi_client_token`
- `clinic_name`
- `clinic_phone`

## ✅ Solução

### Método 1: Via Dashboard do Vercel (Recomendado)

1. **Acesse o Dashboard do Vercel**
   - Vá para [vercel.com/dashboard](https://vercel.com/dashboard)
   - Selecione seu projeto `chatbot-clincia`

2. **Configure as Variáveis de Ambiente**
   - Vá para **Settings** → **Environment Variables**
   - Clique em **Add New**
   - Configure cada variável:

#### Z-API Configuration
```
ZAPI_INSTANCE_ID = 3E4F7360B552F0C2DBCB9E6774402775
ZAPI_TOKEN = F909fc109aad54566bf42a6d09f00a8dbS
ZAPI_CLIENT_TOKEN = F909fc109aad54566bf42a6d09f00a8dbS
ZAPI_BASE_URL = https://api.z-api.io
```

#### Supabase Configuration
```
SUPABASE_URL = https://feqylqrphdpeeusdyeyw.supabase.co
SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NzQwOTksImV4cCI6MjA2OTQ1MDA5OX0.cavDpXtpWn28D_FN6prGFjXATj8DdaUPdG7Rrd-m_kI
SUPABASE_SERVICE_ROLE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcXlscXJwaGRwZWV1c2R5ZXl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzg3NDA5OSwiZXhwIjoyMDY5NDUwMDk5fQ.gEF_cKRzAtDklZuTueVX_1XzaFrGONzECBS4tt13uIc
```

#### GestãoDS Configuration
```
GESTAODS_API_URL = https://apidev.gestaods.com.br
GESTAODS_TOKEN = 733a8e19a94b65d58390da380ac946b6d603a535
```

#### App Configuration
```
ENVIRONMENT = production
DEBUG = false
CORS_ORIGINS = *
CORS_ALLOW_CREDENTIALS = true
```

#### Clinic Information
```
CLINIC_NAME = Clínica Gabriela Nassif
CLINIC_PHONE = 5531999999999
REMINDER_HOUR = 18
REMINDER_MINUTE = 0
```

#### WebSocket Configuration
```
WEBSOCKET_ENABLED = true
WEBSOCKET_MAX_CONNECTIONS = 50
```

3. **Importante**: Para cada variável, certifique-se de:
   - ✅ Marcar **Production** 
   - ✅ Marcar **Preview** (opcional)
   - ✅ Marcar **Development** (opcional)

4. **Deploy Novamente**
   - Após configurar todas as variáveis, faça um novo deploy
   - Vá para **Deployments** e clique em **Redeploy** no último deployment

### Método 2: Via Vercel CLI

1. **Instale o Vercel CLI** (se não tiver):
   ```bash
   npm i -g vercel
   ```

2. **Faça login**:
   ```bash
   vercel login
   ```

3. **Execute o script de configuração**:
   ```bash
   python vercel_setup_env.py
   ```

4. **Deploy**:
   ```bash
   vercel --prod
   ```

### Método 3: Configuração Manual via CLI

Para cada variável, execute:

```bash
vercel env add ZAPI_INSTANCE_ID production
# Digite: 3E4F7360B552F0C2DBCB9E6774402775

vercel env add ZAPI_TOKEN production
# Digite: F909fc109aad54566bf42a6d09f00a8dbS

vercel env add ZAPI_CLIENT_TOKEN production
# Digite: F909fc109aad54566bf42a6d09f00a8dbS

vercel env add CLINIC_NAME production
# Digite: Clínica Gabriela Nassif

vercel env add CLINIC_PHONE production
# Digite: 5531999999999
```

## 🔍 Verificação

Após configurar as variáveis:

1. **Verifique no Dashboard**:
   - Settings → Environment Variables
   - Confirme que todas as variáveis estão listadas

2. **Teste o Deploy**:
   - Faça um novo deploy
   - Verifique os logs para confirmar que não há mais erros

3. **Teste a Aplicação**:
   - Acesse: `https://chatbot-clincia.vercel.app/`
   - Deve retornar uma resposta JSON com status "online"

## 🚨 Troubleshooting

### Se ainda houver erros:

1. **Verifique se todas as variáveis estão configuradas**
2. **Confirme que estão marcadas para Production**
3. **Aguarde alguns minutos após o deploy**
4. **Verifique os logs novamente**

### Logs de Sucesso Esperados:

```
✅ Configurações carregadas com sucesso
✅ Usando configurações Pydantic
✅ Aplicação iniciada com sucesso
```

## 📞 Suporte

Se ainda houver problemas:

1. Verifique os logs em: `https://vercel.com/dashboard/[seu-projeto]/functions`
2. Confirme que todas as variáveis estão configuradas corretamente
3. Tente fazer um deploy limpo (remova o cache se necessário) 