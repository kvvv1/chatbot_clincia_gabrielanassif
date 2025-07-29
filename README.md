# 🤖 Chatbot Clínica Gabriela Nassif

Assistente virtual no WhatsApp para automatizar o atendimento da Clínica Gabriela Nassif, integrado com o sistema GestãoDS.

## 🎯 Funcionalidades

- ✅ **Agendamento Automático**: Agendar consultas via WhatsApp
- ✅ **Lembretes Inteligentes**: Envio automático 24h antes da consulta
- ✅ **Gestão de Cancelamentos**: Cancelamento e reagendamento
- ✅ **Lista de Espera**: Sistema inteligente de notificação
- ✅ **Integração GestãoDS**: Sincronização completa com o sistema principal
- ✅ **Validação de CPF**: Verificação automática de pacientes

## 🏗️ Arquitetura

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│                 │     │              │     │                 │
│  WhatsApp       │────▶│   Z-API      │────▶│  FastAPI        │
│  (Paciente)     │◀────│  (Webhook)   │◀────│  (Backend)      │
│                 │     │              │     │                 │
└─────────────────┘     └──────────────┘     └────────┬────────┘
                                                       │
                                                       ▼
                        ┌──────────────┐     ┌─────────────────┐
                        │              │     │                 │
                        │  PostgreSQL  │◀────┤  GestãoDS API   │
                        │  (Cache)     │     │  (REST)         │
                        │              │     │                 │
                        └──────────────┘     └─────────────────┘
```

## 🚀 Stack Tecnológica

- **Backend**: Python 3.11 + FastAPI
- **WhatsApp**: Z-API (sem necessidade de aprovação Meta)
- **Banco de Dados**: PostgreSQL
- **Deploy**: Docker + Railway/Render
- **Agendador**: APScheduler
- **HTTP Client**: httpx (assíncrono)

## 📋 Pré-requisitos

- Python 3.11+
- PostgreSQL
- Conta Z-API
- Acesso à API GestãoDS

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/chatbot-clinica.git
cd chatbot-clinica
```

### 2. Configure o ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Mac/Linux)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Z-API Credentials
ZAPI_INSTANCE_ID=seu_instance_id
ZAPI_TOKEN=seu_token
ZAPI_CLIENT_TOKEN=seu_client_token

# GestãoDS API
GESTAODS_API_URL=https://apidev.gestaods.com.br
GESTAODS_TOKEN=seu_token_gestaods

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_clinica

# App Settings
APP_HOST=0.0.0.0
APP_PORT=8000
ENVIRONMENT=development
DEBUG=True

# Clinic Info
CLINIC_NAME=Clínica Gabriela Nassif
CLINIC_PHONE=5531999999999
REMINDER_HOUR=18
REMINDER_MINUTE=0
```

### 4. Configure o banco de dados

```bash
# Criar banco PostgreSQL
createdb chatbot_clinica

# As tabelas serão criadas automaticamente na primeira execução
```

### 5. Execute a aplicação

```bash
# Desenvolvimento
uvicorn app.main:app --reload

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🐳 Docker

### Desenvolvimento local

```bash
# Usando docker-compose
docker-compose up --build

# Acesse: http://localhost:8000
```

### Produção

```bash
# Build da imagem
docker build -t chatbot-clinica .

# Executar container
docker run -p 8000:8000 --env-file .env chatbot-clinica
```

## 🔧 Configuração Z-API

### 1. Criar conta Z-API

1. Acesse https://app.z-api.io/
2. Clique em "Crie uma conta grátis"
3. Complete o cadastro

### 2. Configurar instância WhatsApp

1. No painel Z-API, clique em "Nova Instância"
2. Escolha um nome (ex: "clinica-gabriela")
3. Conecte o WhatsApp:
   - Abra WhatsApp no celular
   - Vá em Configurações → Dispositivos conectados
   - Escaneie o QR Code

### 3. Configurar webhooks

No painel da instância:

1. Clique em "Editar" → "Webhooks"
2. Configure as URLs:
   - **Webhook de Mensagens Recebidas**: `https://seu-dominio.com/webhook/message`
   - **Webhook de Status**: `https://seu-dominio.com/webhook/status`
   - **Webhook de Conexão**: `https://seu-dominio.com/webhook/connected`

### 4. Obter credenciais

1. Na aba "Segurança", copie:
   - **Instance ID**
   - **Token**
   - **Client Token**

## 📱 Fluxo de Conversa

### Menu Principal
```
🏥 Clínica Gabriela Nassif

Como posso ajudar você hoje?

1️⃣ - Agendar consulta
2️⃣ - Ver meus agendamentos
3️⃣ - Cancelar consulta
4️⃣ - Lista de espera
5️⃣ - Falar com atendente
```

### Processo de Agendamento
1. **Validação de CPF**: Verifica se o paciente está cadastrado
2. **Escolha de Data**: Mostra próximos 7 dias úteis
3. **Escolha de Horário**: Lista horários disponíveis
4. **Confirmação**: Resumo do agendamento
5. **Confirmação**: Salva no GestãoDS + envia confirmação

## 🔄 Tarefas Automáticas

### Lembretes Diários
- **Horário**: 18:00 (configurável)
- **Função**: Envia lembretes para consultas do dia seguinte
- **Frequência**: Diária

### Verificação de Cancelamentos
- **Frequência**: A cada 30 minutos
- **Função**: Notifica lista de espera sobre vagas disponíveis

## 📊 Endpoints da API

### Saúde da Aplicação
- `GET /` - Status básico
- `GET /health` - Verificação detalhada

### Webhooks Z-API
- `POST /webhook/message` - Mensagens recebidas
- `POST /webhook/status` - Status das mensagens
- `POST /webhook/connected` - Status de conexão

## 🧪 Testes

```bash
# Executar testes
pytest

# Executar com cobertura
pytest --cov=app
```

## 📝 Logs

Os logs são salvos em:
- **Arquivo**: `chatbot.log`
- **Console**: Saída padrão
- **Nível**: INFO

## 🚀 Deploy

### Railway
1. Conecte seu repositório GitHub
2. Configure as variáveis de ambiente
3. Deploy automático

### Render
1. Crie novo Web Service
2. Conecte repositório
3. Configure variáveis de ambiente
4. Deploy

## 🔒 Segurança

- Validação de CPF brasileiro
- Sanitização de inputs
- Logs de auditoria
- Rate limiting (implementar)
- Autenticação de webhooks (implementar)

## 📈 Monitoramento

### Métricas importantes
- Mensagens processadas/minuto
- Taxa de sucesso de agendamentos
- Tempo de resposta da API
- Status do WhatsApp

### Alertas
- WhatsApp desconectado
- Erro na API GestãoDS
- Falha no envio de lembretes

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte técnico:
- **Email**: suporte@clinica.com
- **WhatsApp**: (31) 9999-9999
- **Documentação**: [Link para docs]

---

**Desenvolvido com ❤️ para a Clínica Gabriela Nassif** 