# 🎯 Guia Final - Configuração do Webhook no Z-API

## 📋 Status Atual

✅ **Sistema Local**: 100% Funcionando
✅ **Supabase**: Conectado e funcionando  
✅ **Z-API**: Enviando mensagens com sucesso
✅ **Webhook Local**: Processando mensagens corretamente
✅ **Vercel**: Endpoints respondendo (307 redirect é normal)

## 🔧 Configuração Manual do Webhook

### Passo 1: Acessar o Painel do Z-API
1. Acesse: https://app.z-api.io/
2. Faça login na sua conta
3. Vá para "Instâncias" no menu lateral
4. Clique na instância: `3E4F7360B552F0C2DBCB9E6774402775`

### Passo 2: Configurar Webhook
Na aba "Webhook" ou "Configurações":

**URLs para configurar:**
- **Ao receber**: `https://chatbot-clincia.vercel.app/webhook/message`
- **Ao enviar**: `https://chatbot-clincia.vercel.app/webhook`
- **Ao conectar**: `https://chatbot-clincia.vercel.app/webhook/connected`
- **Ao desconectar**: `https://chatbot-clincia.vercel.app/webhook`
- **Receber status da mensagem**: `https://chatbot-clincia.vercel.app/webhook/status`

**Configurações importantes:**
- ✅ Ativar "Notificar as enviadas por mim também"
- ✅ Ativar todos os eventos
- ✅ Salvar configurações

## 🚀 Deploy no Vercel

### Passo 3: Fazer Deploy
```bash
# Deploy em produção
npx vercel --prod
```

### Passo 4: Verificar Deploy
- Acesse: https://chatbot-clincia.vercel.app/
- Deve retornar status 200 ou 307 (redirect)

## 🧪 Teste Completo do Sistema

### Passo 5: Testar Endpoints
```bash
# Testar endpoints do Vercel
curl https://chatbot-clincia.vercel.app/
curl https://chatbot-clincia.vercel.app/webhook
curl https://chatbot-clincia.vercel.app/webhook/message
```

### Passo 6: Testar Webhook
```bash
# Testar webhook com dados simulados
curl -X POST https://chatbot-clincia.vercel.app/webhook/message \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message",
    "data": {
      "id": "test_123",
      "type": "text",
      "from": "553198600366@c.us",
      "fromMe": false,
      "text": {
        "body": "1"
      }
    }
  }'
```

### Passo 7: Testar Mensagem Real
1. Envie uma mensagem para o WhatsApp da clínica
2. Verifique se o webhook recebe e processa
3. Verifique se a resposta é enviada

## 📊 Monitoramento

### Logs do Vercel
- Acesse: https://vercel.com/dashboard
- Vá para o projeto chatbot-clincia
- Verifique os logs em tempo real

### Logs do Z-API
- No painel do Z-API, verifique os logs de webhook
- Confirme se as requisições estão chegando

### Logs do Supabase
- Acesse: https://supabase.com/dashboard
- Verifique se os dados estão sendo salvos

## 🔧 Variáveis de Ambiente no Vercel

Configure no painel do Vercel:
```env
SUPABASE_URL=https://feqylqrphdpeeusdyeyw.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ZAPI_INSTANCE_ID=3E4F7360B552F0C2DBCB9E6774402775
ZAPI_TOKEN=17829E98BB59E9ADD55BBBA9
ZAPI_CLIENT_TOKEN=F909fc109aad54566bf42a6d09f00a8dbS
ZAPI_BASE_URL=https://api.z-api.io
ENVIRONMENT=production
```

## ✅ Checklist Final

- [ ] Deploy no Vercel realizado
- [ ] Endpoints respondendo corretamente
- [ ] Webhook configurado manualmente no Z-API
- [ ] Mensagem de teste enviada
- [ ] Resposta recebida no WhatsApp
- [ ] Dados salvos no Supabase
- [ ] Logs funcionando
- [ ] Sistema 100% operacional

## 🎉 Sistema Pronto!

Após seguir todos os passos, o sistema estará 100% funcional e pronto para:
- ✅ Receber mensagens do WhatsApp
- ✅ Processar conversas automaticamente
- ✅ Enviar respostas personalizadas
- ✅ Salvar dados no Supabase
- ✅ Gerenciar agendamentos

**🚀 Sistema de Chatbot da Clínica Nassif - ONLINE!**

## 🚨 Troubleshooting

### Problema: Webhook não recebe mensagens
**Solução:**
1. Verificar se o Z-API está conectado
2. Verificar se as URLs do webhook estão corretas
3. Verificar logs do Vercel

### Problema: Mensagens não são processadas
**Solução:**
1. Verificar logs do ConversationManager
2. Verificar conexão com Supabase
3. Verificar variáveis de ambiente

### Problema: Respostas não são enviadas
**Solução:**
1. Verificar credenciais do Z-API
2. Verificar se a instância está conectada
3. Verificar logs de envio 