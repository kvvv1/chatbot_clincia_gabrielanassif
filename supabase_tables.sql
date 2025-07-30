-- =====================================================
-- TABELAS NECESSÁRIAS PARA O CHATBOT
-- Execute este SQL no SQL Editor do Supabase
-- =====================================================

-- Tabela de conversas
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    state VARCHAR(50) DEFAULT 'inicio',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para conversas
CREATE INDEX IF NOT EXISTS idx_conversations_phone ON conversations(phone);
CREATE INDEX IF NOT EXISTS idx_conversations_state ON conversations(state);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at);

-- Tabela de agendamentos
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    patient_cpf VARCHAR(14),
    patient_name VARCHAR(255),
    appointment_date TIMESTAMP WITH TIME ZONE,
    appointment_time VARCHAR(10),
    status VARCHAR(20) DEFAULT 'agendado',
    gestaods_id INTEGER,
    reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para agendamentos
CREATE INDEX IF NOT EXISTS idx_appointments_cpf ON appointments(patient_cpf);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_reminder_sent ON appointments(reminder_sent);

-- Tabela de lista de espera
CREATE TABLE IF NOT EXISTS waiting_list (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    patient_cpf VARCHAR(14),
    patient_name VARCHAR(255),
    preferred_date DATE,
    preferred_time VARCHAR(10),
    status VARCHAR(20) DEFAULT 'aguardando',
    priority INTEGER DEFAULT 0,
    notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para lista de espera
CREATE INDEX IF NOT EXISTS idx_waiting_list_cpf ON waiting_list(patient_cpf);
CREATE INDEX IF NOT EXISTS idx_waiting_list_status ON waiting_list(status);
CREATE INDEX IF NOT EXISTS idx_waiting_list_priority ON waiting_list(priority);
CREATE INDEX IF NOT EXISTS idx_waiting_list_notified ON waiting_list(notified);

-- Tabela de logs de mensagens
CREATE TABLE IF NOT EXISTS message_logs (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    message_id VARCHAR(100),
    direction VARCHAR(10) CHECK (direction IN ('in', 'out')),
    message_type VARCHAR(20),
    content TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para logs de mensagens
CREATE INDEX IF NOT EXISTS idx_message_logs_conversation ON message_logs(conversation_id);
CREATE INDEX IF NOT EXISTS idx_message_logs_created_at ON message_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_message_logs_direction ON message_logs(direction);

-- =====================================================
-- DADOS DE EXEMPLO (OPCIONAL)
-- =====================================================

-- Inserir conversa de exemplo
INSERT INTO conversations (phone, state, context) 
VALUES ('553198600366', 'inicio', '{"test": true}')
ON CONFLICT DO NOTHING;

-- =====================================================
-- VERIFICAÇÃO DAS TABELAS
-- =====================================================

-- Verificar se as tabelas foram criadas
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_name IN ('conversations', 'appointments', 'waiting_list', 'message_logs')
ORDER BY table_name; 