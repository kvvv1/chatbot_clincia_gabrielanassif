# 🤖 Guia Completo - Configuração do Webhook Z-API

## 📋 Visão Geral

Este guia te ajudará a configurar completamente o webhook do Z-API e testar todo o sistema integrado do chatbot da clínica.

## 🚀 Passos para Configuração

### 1. Verificar Configurações Atuais

As seguintes variáveis de ambiente já estão configuradas no Vercel:

```env
ZAPI_INSTANCE_ID=3E4F7360B552F0C2DBCB9E6774402775
ZAPI_TOKEN=17829E98BB59E9ADD55BBBA9
ZAPI_CLIENT_TOKEN=17829E98BB59E9ADD55BBBA9
ZAPI_BASE_URL=https://api.z-api.io
```

### 2. Configurar Webhook no Z-API

#### Opção A: Usando o Script Automático

```bash
# Instalar dependências
pip install httpx python-dotenv

# Executar script de configuração
python configure_webhook.py
```

#### Opção B: Configuração Manual

1. Acesse o painel do Z-API
2. Vá para sua instância
3. Configure o webhook com a URL: `https://chatbot-clincia.vercel.app/webhook`
4. Ative os eventos:
   - ✅ Mensagens recebidas
   - ✅ Conexão/Desconexão
   - ✅ Status das mensagens

### 3. Testar o Sistema Completo

```bash
# Executar testes completos
python test_complete_system.py
```

## 🔧 Endpoints Disponíveis

### Backend (Vercel)
- **URL Base**: `https://chatbot-clincia.vercel.app`
- **Health Check**: `GET /`
- **Test**: `GET /test`

### Webhook
- **Teste**: `GET /webhook/test`
- **Configurar**: `GET /webhook/configure`
- **Status**: `GET /webhook/status`
- **Teste Mensagem**: `POST /webhook/test-message`

### Dashboard
- **Health**: `GET /dashboard/health`
- **Conversas**: `GET /dashboard/conversations`
- **Analytics**: `GET /dashboard/analytics`
- **Agendamentos**: `GET /dashboard/appointments`

## 📱 Frontend Dashboard

### Acessar o Dashboard
- **URL**: `https://chatbot-clincia.vercel.app/dashboard`
- **Desenvolvimento**: `http://localhost:3000`

### Funcionalidades
- ✅ Visualizar conversas em tempo real
- ✅ Ver estados das conversas
- ✅ Enviar mensagens manualmente
- ✅ Analytics e estatísticas
- ✅ Filtros e busca

## 🧪 Testes Disponíveis

### 1. Teste de Saúde do Backend
```bash
curl https://chatbot-clincia.vercel.app/
```

### 2. Teste do Webhook
```bash
curl https://chatbot-clincia.vercel.app/webhook/test
```

### 3. Teste de Processamento de Mensagem
```bash
curl -X POST https://chatbot-clincia.vercel.app/webhook/test-message
```

### 4. Teste do Dashboard
```bash
curl https://chatbot-clincia.vercel.app/dashboard/health
```

## 🔄 Fluxo de Funcionamento

### 1. Recebimento de Mensagem
1. Usuário envia mensagem no WhatsApp
2. Z-API recebe a mensagem
3. Z-API envia webhook para nosso backend
4. Backend processa a mensagem
5. ConversationManager determina resposta
6. Resposta é enviada via Z-API

### 2. Estados das Conversas
- `inicio` - Estado inicial
- `menu_principal` - Menu de opções
- `aguardando_cpf` - Aguardando CPF do paciente
- `escolhendo_data` - Escolhendo data da consulta
- `escolhendo_horario` - Escolhendo horário
- `confirmando_agendamento` - Confirmando agendamento
- `visualizando_agendamentos` - Visualizando agendamentos
- `cancelando_consulta` - Cancelando consulta
- `lista_espera` - Lista de espera

## 📊 Monitoramento

### Logs do Vercel
- Acesse o painel do Vercel
- Vá para o projeto `chatbot-clincia`
- Clique em "Functions" para ver logs

### Dashboard em Tempo Real
- Acesse o dashboard para ver conversas ativas
- WebSocket mantém conexão em tempo real
- Indicadores de status mostram atividade

## 🛠️ Solução de Problemas

### Problema: Webhook não recebe mensagens
**Solução:**
1. Verificar se o webhook está configurado no Z-API
2. Testar endpoint: `GET /webhook/test`
3. Verificar logs do Vercel

### Problema: Backend não responde
**Solução:**
1. Verificar health check: `GET /`
2. Verificar variáveis de ambiente
3. Verificar logs do Vercel

### Problema: Dashboard não carrega
**Solução:**
1. Verificar se o frontend está rodando
2. Verificar CORS no backend
3. Verificar console do navegador

### Problema: Mensagens não são processadas
**Solução:**
1. Verificar logs do ConversationManager
2. Testar processamento: `POST /webhook/test-message`
3. Verificar conexão com banco de dados

## 📈 Próximos Passos

### 1. Teste Completo
```bash
# Executar todos os testes
python test_complete_system.py
```

### 2. Enviar Mensagem de Teste
```bash
# Usar o script para enviar mensagem
python configure_webhook.py
# Escolher opção 3
```

### 3. Monitorar Dashboard
- Acessar dashboard
- Verificar se conversas aparecem
- Testar envio de mensagens

### 4. Configurar Alertas
- Configurar notificações para erros
- Monitorar performance
- Configurar backups

## 🔗 Links Úteis

- **Backend**: https://chatbot-clincia.vercel.app
- **Dashboard**: https://chatbot-clincia.vercel.app/dashboard
- **Z-API Docs**: https://developer.z-api.io/
- **Vercel Dashboard**: https://vercel.com/dashboard

## 📞 Suporte

Se encontrar problemas:
1. Verificar logs do Vercel
2. Executar testes automatizados
3. Verificar configurações do Z-API
4. Consultar este guia

---

**🎉 Sistema configurado e pronto para uso!** 