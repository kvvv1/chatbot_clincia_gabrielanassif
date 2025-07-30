# ⚙️ Configuração de Variáveis de Ambiente no Vercel

## 🚀 PASSO 1: Acesse o Dashboard do Vercel

1. Vá para: https://vercel.com/dashboard
2. Selecione seu projeto: **chatbot-nassif**
3. Clique em **Settings** (Configurações)
4. Clique em **Environment Variables** na barra lateral

## 🔑 PASSO 2: Adicione as Variáveis de Ambiente

Adicione cada uma dessas variáveis **EXATAMENTE** como mostrado:

### Z-API (WhatsApp) - OBRIGATÓRIAS ✅
```
ZAPI_INSTANCE_ID=3E4F7360B552F0C2DBCB9E6774402775
ZAPI_TOKEN=17829E98BB59E9ADD55BBBA9
ZAPI_CLIENT_TOKEN=17829E98BB59E9ADD55BBBA9
```

### Configurações da Clínica - OBRIGATÓRIAS ✅
```
CLINIC_NAME=Clínica Nassif
CLINIC_PHONE=
```

### Supabase (Opcional - pode deixar vazio) ⚪
```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

### Configurações do Sistema ✅
```
ENVIRONMENT=production
VERCEL=1
```

## 🔧 PASSO 3: Como Adicionar no Vercel

Para cada variável:

1. Clique em **"Add"** ou **"Add Environment Variable"**
2. **Name**: Cole o nome da variável (ex: `ZAPI_INSTANCE_ID`)
3. **Value**: Cole o valor correspondente (ex: `3E4F7360B552F0C2DBCB9E6774402775`)
4. **Environments**: Selecione **"Production"**, **"Preview"** e **"Development"**
5. Clique em **"Save"**

## 🚀 PASSO 4: Fazer Redeploy

Após adicionar todas as variáveis:

1. Vá para a aba **"Deployments"**
2. Clique nos **três pontos (...)** do deployment mais recente
3. Clique em **"Redeploy"**
4. Aguarde o deploy terminar (geralmente 1-2 minutos)

## ✅ PASSO 5: Testar

Após o redeploy, teste os endpoints:

- https://chatbot-nassif.vercel.app/
- https://chatbot-nassif.vercel.app/health
- https://chatbot-nassif.vercel.app/debug

## 🆘 Se Ainda Houver Problemas

Se o erro persistir, verifique:

1. ✅ Todas as variáveis foram adicionadas corretamente
2. ✅ Não há espaços extras nos valores
3. ✅ O redeploy foi feito após adicionar as variáveis
4. ✅ Aguarde alguns minutos para propagação

## 📞 Próximos Passos

Após funcionar, você poderá:
- Configurar o webhook do WhatsApp
- Testar o chatbot
- Configurar o Supabase (se necessário)