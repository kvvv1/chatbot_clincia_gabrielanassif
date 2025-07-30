# 🗄️ Configuração Supabase - Chatbot Clínica

## 📋 Passo a Passo

### 1. **Criar conta no Supabase**
1. Acessar https://supabase.com
2. Clicar em "Start your project"
3. Fazer login com GitHub ou criar conta

### 2. **Criar novo projeto**
1. Clicar em "New Project"
2. Escolher organização (ou criar uma)
3. **Nome do projeto**: `chatbot-clinica`
4. **Database Password**: Gerar senha forte (anotar!)
5. **Region**: `São Paulo (Brazil)` ou `US East (N. Virginia)`
6. Clicar em "Create new project"

### 3. **Obter credenciais**
Após criar o projeto, você encontrará:

**Settings > API**
- **Project URL**: `https://seu-projeto.supabase.co`
- **anon public**: `sua_chave_anonima_aqui`
- **service_role secret**: `sua_chave_service_role_aqui`

### 4. **Configurar tabelas**
No SQL Editor do Supabase, executar:

```sql
-- Tabela de conversas
CREATE TABLE conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone VARCHAR NOT NULL,
    state VARCHAR DEFAULT 'inicio',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de agendamentos
CREATE TABLE appointments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id VARCHAR NOT NULL,
    patient_name VARCHAR,
    patient_phone VARCHAR,
    appointment_date TIMESTAMP WITH TIME ZONE,
    appointment_type VARCHAR,
    status VARCHAR DEFAULT 'scheduled',
    reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de lista de espera
CREATE TABLE waiting_list (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id VARCHAR NOT NULL,
    patient_name VARCHAR,
    patient_phone VARCHAR,
    preferred_dates JSONB,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notified BOOLEAN DEFAULT FALSE
);

-- Índices para performance
CREATE INDEX idx_conversations_phone ON conversations(phone);
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_waiting_list_patient_id ON waiting_list(patient_id);

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para conversations
CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 5. **Configurar RLS (Row Level Security)**
```sql
-- Habilitar RLS
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE waiting_list ENABLE ROW LEVEL SECURITY;

-- Políticas para acesso público (para o bot)
CREATE POLICY "Enable read access for all users" ON conversations FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON conversations FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON conversations FOR UPDATE USING (true);

CREATE POLICY "Enable read access for all users" ON appointments FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON appointments FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON appointments FOR UPDATE USING (true);

CREATE POLICY "Enable read access for all users" ON waiting_list FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON waiting_list FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON waiting_list FOR UPDATE USING (true);
```

## 🔧 Configuração no Código

### 1. **Atualizar variáveis de ambiente**
```env
# Supabase (Produção)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_anonima_aqui
SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role_aqui
```

### 2. **Testar conexão**
```bash
python test_supabase.py
```

## 📊 Monitoramento

### **Dashboard do Supabase**
- **Database**: Ver tabelas e dados
- **API**: Testar endpoints
- **Logs**: Verificar erros
- **Auth**: Gerenciar usuários (se necessário)

### **Métricas importantes**
- **Storage**: Uso de armazenamento
- **Bandwidth**: Tráfego de dados
- **API Calls**: Número de requisições
- **Database Size**: Tamanho do banco

## 🚨 Troubleshooting

### **Problemas comuns:**
1. **Erro de conexão**: Verificar URL e chave
2. **Erro de permissão**: Verificar RLS policies
3. **Erro de schema**: Verificar se tabelas foram criadas
4. **Timeout**: Verificar região do projeto

### **Comandos úteis:**
```sql
-- Verificar tabelas
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Verificar dados
SELECT COUNT(*) FROM conversations;
SELECT COUNT(*) FROM appointments;
SELECT COUNT(*) FROM waiting_list;

-- Limpar dados de teste
DELETE FROM conversations WHERE phone LIKE '%test%';
DELETE FROM appointments WHERE patient_name LIKE '%test%';
```

## 📞 Suporte

- **Documentação**: https://supabase.com/docs
- **Discord**: https://discord.supabase.com
- **GitHub**: https://github.com/supabase/supabase 