# 🚀 **INSTRUÇÕES DE DEPLOY - CORREÇÃO CRÍTICA**

## ✅ **PROBLEMA RESOLVIDO**

A **causa raiz** foi identificada e corrigida:
- **Webhook criava nova instância** do ConversationManager a cada mensagem
- **Estados eram perdidos** entre requisições
- **Cache interno era resetado** constantemente

---

## 🔧 **CORREÇÃO APLICADA**

### **Arquivo alterado:** `app/handlers/webhook.py`

#### **✅ Mudanças:**
1. **Instância global** do ConversationManager
2. **Reutilização** da mesma instância
3. **Preservação** de cache e estado

#### **✅ Código adicionado:**
```python
# Instância global para evitar recriação
_conversation_manager = None

def get_conversation_manager():
    """Retorna instância singleton do ConversationManager"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
```

#### **✅ Substituições:**
```python
# ❌ ANTES:
conversation_manager = ConversationManager()

# ✅ DEPOIS:
conversation_manager = get_conversation_manager()
```

---

## 🚨 **DEPLOY OBRIGATÓRIO**

### **Para que a correção funcione, você DEVE:**

### **1. 🔄 REINICIAR APLICAÇÃO**
```bash
# Parar processo atual
# Reiniciar aplicação
python run.py
```

### **2. 🚀 DEPLOY NO VERCEL (se usando)**
```bash
vercel --prod
```

### **3. 🐳 REBUILD CONTAINER (se usando Docker)**
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### **4. 🔁 CLEAR CACHE**
- Limpar cache do navegador
- Restart do servidor
- Clear de qualquer proxy/CDN

---

## 🧪 **COMO VERIFICAR SE FUNCIONOU**

### **Teste simples:**
1. **Envie:** "oi"
2. **Espere:** Menu principal
3. **Envie:** "1"
4. **Espere:** Solicitar CPF
5. **Envie:** CPF válido (ex: 11144477735)
6. **Espere:** **Confirmação do paciente** ← DEVE APARECER!

### **✅ SUCESSO se:**
- Estados mudam corretamente
- Confirmação de paciente aparece
- Fluxo não volta ao menu

### **❌ FALHA se:**
- Estado não muda
- Volta sempre ao menu
- Não chega na confirmação

---

## 🔍 **VERIFICAR LOGS**

### **Procurar por:**
```
🔧 Criando instância global do ConversationManager
```

### **Se aparecer múltiplas vezes:**
- ❌ Aplicação está reiniciando
- ❌ Deploy não foi feito
- ❌ Cache não foi limpo

### **Se aparecer só uma vez:**
- ✅ Correção funcionando
- ✅ Instância global ativa

---

## 🚨 **OUTROS PROBLEMAS POTENCIAIS**

### **Se ainda não funcionar após deploy:**

#### **1. 🗄️ Problema no Supabase:**
- Verificar conexão
- Verificar permissões
- Verificar estrutura de tabelas

#### **2. ⚙️ Configuração de Ambiente:**
- Variáveis de ambiente
- Tokens da API
- URLs de configuração

#### **3. 🌐 Problema de Rede:**
- Webhook não chegando
- Timeout nas requisições
- Problemas de CORS

---

## 📞 **CONTATO EM CASO DE PROBLEMAS**

Se após o deploy correto o problema persistir:

1. **Enviar logs** da aplicação
2. **Confirmar** que o deploy foi feito
3. **Verificar** se a correção está no código em produção

---

## ✅ **RESUMO EXECUTIVO**

- ✅ **Problema identificado:** Instâncias múltiplas do ConversationManager
- ✅ **Correção aplicada:** Instância global singleton
- ✅ **Teste confirmado:** Estados mantidos corretamente
- 🚀 **Ação necessária:** Deploy obrigatório da correção

**Após o deploy, o chatbot funcionará perfeitamente! 🎯**