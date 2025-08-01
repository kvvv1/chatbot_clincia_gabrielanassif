# 🔧 CONFIGURAÇÃO COMPLETA DOS WEBHOOKS Z-API

## 📋 Status Atual
- ✅ **Instance ID**: 3E4F7360B552F0C2DBCB9E6774402775
- ✅ **Token**: 17829E98BB59E9ADD55BBBA9
- ✅ **Client Token**: Fb79b25350a784c8e83d4a25213955ab5S
- ✅ **URL Base**: https://chatbot-clincia.vercel.app

## 🎯 Webhooks Necessários (5 Tipos)

### 1️⃣ **AO ENVIAR** 
- **URL**: `https://chatbot-clincia.vercel.app/webhook/status`
- **Função**: Recebe confirmação quando uma mensagem é enviada pelo chatbot
- **Endpoint**: `/webhook/status` (POST)
- **Status**: ⚠️ Precisa ser configurado

### 2️⃣ **AO DESCONECTAR**
- **URL**: `https://chatbot-clincia.vercel.app/webhook/connected`
- **Função**: Recebe notificação quando o WhatsApp é desconectado
- **Endpoint**: `/webhook/connected` (POST)
- **Status**: ⚠️ Precisa ser configurado

### 3️⃣ **RECEBER STATUS DA MENSAGEM**
- **URL**: `https://chatbot-clincia.vercel.app/webhook/status`
- **Função**: Recebe status de entrega, leitura, etc.
- **Endpoint**: `/webhook/status` (POST)
- **Status**: ⚠️ Precisa ser configurado

### 4️⃣ **AO RECEBER**
- **URL**: `https://chatbot-clincia.vercel.app/webhook/message`
- **Função**: Recebe mensagens enviadas pelos clientes
- **Endpoint**: `/webhook/message` (POST)
- **Status**: ⚠️ Precisa ser configurado

### 5️⃣ **AO CONECTAR**
- **URL**: `https://chatbot-clincia.vercel.app/webhook/connected`
- **Função**: Recebe notificação quando o WhatsApp é conectado
- **Endpoint**: `/webhook/connected` (POST)
- **Status**: ⚠️ Precisa ser configurado

## 🔧 Configuração Manual no Painel Z-API

### Passo 1: Acessar o Painel
1. Acesse: https://app.z-api.io/
2. Faça login na sua conta
3. Vá para "Instâncias"
4. Clique na instância: `3E4F7360B552F0C2DBCB9E6774402775`

### Passo 2: Configurar Webhooks
Na aba "Webhook" ou "Configurações":

#### ✅ AO ENVIAR
```
URL: https://chatbot-clincia.vercel.app/webhook/status
Descrição: Confirmação de envio de mensagens
```

#### ✅ AO DESCONECTAR
```
URL: https://chatbot-clincia.vercel.app/webhook/connected
Descrição: Notificação de desconexão do WhatsApp
```

#### ✅ RECEBER STATUS DA MENSAGEM
```
URL: https://chatbot-clincia.vercel.app/webhook/status
Descrição: Status de entrega e leitura
```

#### ✅ AO RECEBER
```
URL: https://chatbot-clincia.vercel.app/webhook/message
Descrição: Mensagens recebidas dos clientes
```

#### ✅ AO CONECTAR
```
URL: https://chatbot-clincia.vercel.app/webhook/connected
Descrição: Notificação de conexão do WhatsApp
```

### Passo 3: Configurações Adicionais
- ✅ **Ativar**: "Notificar as enviadas por mim também"
- ✅ **Ativar**: Todos os eventos
- ✅ **Salvar**: Configurações

## 🧪 Teste dos Endpoints

### Verificar se os endpoints estão funcionando:

```bash
# Teste 1: Health Check
curl https://chatbot-clincia.vercel.app/

# Teste 2: Webhook Principal
curl https://chatbot-clincia.vercel.app/webhook

# Teste 3: Webhook Mensagens
curl https://chatbot-clincia.vercel.app/webhook/message

# Teste 4: Webhook Status
curl https://chatbot-clincia.vercel.app/webhook/status

# Teste 5: Webhook Conexão
curl https://chatbot-clincia.vercel.app/webhook/connected
```

### Teste com dados simulados:

```bash
# Teste de mensagem recebida
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

## 🚀 Configuração Automática

Execute o script para configurar automaticamente:

```bash
python configurar_webhooks_zapi_completo.py
```

## 📊 Estrutura dos Endpoints

### `/webhook/message` (POST)
```python
# Recebe mensagens dos clientes
{
    "event": "message",
    "data": {
        "id": "message_id",
        "type": "text",
        "from": "phone@c.us",
        "fromMe": false,
        "text": {
            "body": "mensagem do cliente"
        }
    }
}
```

### `/webhook/status` (POST)
```python
# Recebe status das mensagens
{
    "event": "status",
    "data": {
        "id": "message_id",
        "status": "delivered|read|sent"
    }
}
```

### `/webhook/connected` (POST)
```python
# Recebe eventos de conexão
{
    "event": "connection",
    "data": {
        "status": "connected|disconnected"
    }
}
```

## 🔍 Verificação de Funcionamento

### 1. Teste de Mensagem Real
1. Envie uma mensagem para o WhatsApp da clínica
2. Verifique se o webhook `/webhook/message` recebe a notificação
3. Verifique se a resposta automática é enviada

### 2. Teste de Status
1. Envie uma mensagem
2. Verifique se o webhook `/webhook/status` recebe confirmação
3. Verifique se o status é "delivered" ou "read"

### 3. Teste de Conexão
1. Desconecte e reconecte o WhatsApp
2. Verifique se o webhook `/webhook/connected` recebe notificação

## ⚠️ Problemas Comuns

### Erro 404 nos endpoints
- Verifique se o deploy no Vercel foi feito corretamente
- Verifique se a URL está correta

### Webhook não recebe notificações
- Verifique se todos os 5 webhooks estão configurados
- Verifique se "Notificar as enviadas por mim também" está ativado

### Mensagens não são processadas
- Verifique os logs do Vercel
- Verifique se o ConversationManager está funcionando

## 📞 Suporte

Se houver problemas:
1. Verifique os logs do Vercel
2. Teste os endpoints individualmente
3. Verifique a configuração no painel Z-API
4. Execute o script de configuração automática

## 🎉 Status Final Esperado

Após a configuração correta:
- ✅ Todos os 5 webhooks configurados
- ✅ Endpoints respondendo corretamente
- ✅ Mensagens sendo processadas
- ✅ Respostas automáticas funcionando
- ✅ Sistema 100% operacional 