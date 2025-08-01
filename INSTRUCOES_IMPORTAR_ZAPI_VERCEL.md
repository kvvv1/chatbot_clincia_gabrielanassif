# 📋 Instruções para Importar Variáveis ZAPI no Vercel

## 🎯 Objetivo
Importar as variáveis de ambiente do ZAPI para o seu projeto no Vercel.

## 📁 Arquivo Criado
- `zapi_vercel_env.json` - Contém todas as variáveis necessárias

## 🚀 Passo a Passo

### 1. Acesse o Dashboard do Vercel
1. Vá para [vercel.com](https://vercel.com)
2. Faça login na sua conta
3. Selecione o projeto do chatbot

### 2. Configure as Variáveis de Ambiente
1. No dashboard do projeto, clique em **Settings**
2. No menu lateral, clique em **Environment Variables**
3. Clique no botão **Import** (se disponível) ou adicione manualmente

### 3. Importação Manual (Recomendado)
Adicione cada variável manualmente:

#### 🔑 Variáveis ZAPI (Obrigatórias)
```
ZAPI_INSTANCE_ID = 3E4F7360B552F0C2DBCB9E6774402775
ZAPI_TOKEN = 0BDEFB65E4B5E5615697BCD6
ZAPI_CLIENT_TOKEN = Fb79b25350a784c8e83d4a25213955ab5S
ZAPI_BASE_URL = https://api.z-api.io
```

#### ⚙️ Configurações do Sistema
```
ENVIRONMENT = production
DEBUG = False
CORS_ORIGINS = *
```

#### 🏥 Informações da Clínica
```
CLINIC_NAME = Clínica Gabriela Nassif
CLINIC_PHONE = 5531999999999
REMINDER_HOUR = 18
REMINDER_MINUTE = 0
```

#### 🔌 Configurações WebSocket
```
WEBSOCKET_ENABLED = true
WEBSOCKET_MAX_CONNECTIONS = 50
```

### 4. Configuração de Ambiente
- **Environment**: Selecione `Production` para todas as variáveis
- **Preview**: Marque se quiser usar em preview deployments
- **Development**: Marque se quiser usar em desenvolvimento local

### 5. Salvar e Deploy
1. Clique em **Save** para cada variável
2. Vá para **Deployments**
3. Clique em **Redeploy** no último deployment

## ✅ Verificação
Após o deploy, você pode verificar se as variáveis estão funcionando:
1. Acesse os logs do deployment
2. Verifique se não há erros de configuração
3. Teste o webhook do WhatsApp

## 🔧 Variáveis Supabase (Adicionais)
Se você ainda não configurou o Supabase, adicione também:
```
SUPABASE_URL = sua_url_do_supabase
SUPABASE_ANON_KEY = sua_chave_anonima
SUPABASE_SERVICE_ROLE_KEY = sua_chave_service_role
```

## 🆘 Suporte
Se encontrar problemas:
1. Verifique se todas as variáveis foram adicionadas
2. Confirme se os valores estão corretos
3. Verifique os logs do deployment
4. Teste a conectividade com o ZAPI

---
**📝 Nota**: Mantenha essas credenciais seguras e não as compartilhe publicamente! 