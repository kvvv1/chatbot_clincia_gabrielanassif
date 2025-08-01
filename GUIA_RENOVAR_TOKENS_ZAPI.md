# 🔄 GUIA COMPLETO - RENOVAR TOKENS Z-API

## 📊 **DIAGNÓSTICO ATUAL**

### ❌ **PROBLEMA IDENTIFICADO**
- **Erro**: `java.lang.NullPointerException` (Erro 500)
- **Causa**: Tokens expirados ou instância com problemas
- **Status**: Tokens precisam ser renovados

### 📋 **TOKENS ATUAIS (COM PROBLEMAS)**
- **Instance ID**: `3E4F7360B552F0C2DBCB9E6774402775`
- **Token**: `17829E98BB59E9ADD55BBBA9` ❌
- **Client Token**: `Fb79b25350a784c8e83d4a25213955ab5S` ✅

## 🔧 **PASSO A PASSO PARA RENOVAR TOKENS**

### **Passo 1: Acessar o Painel Z-API**
1. Acesse: https://app.z-api.io/
2. Faça login na sua conta
3. Vá para "Instâncias"

### **Passo 2: Localizar a Instância**
1. Procure pela instância: `3E4F7360B552F0C2DBCB9E6774402775`
2. Clique na instância para abrir

### **Passo 3: Renovar Tokens**
1. Na instância, vá para a aba **"Segurança"**
2. Procure por **"Renovar Token"** ou **"Regenerate Token"**
3. Clique em **"Renovar"** ou **"Regenerate"**
4. **⚠️ ATENÇÃO**: Isso irá invalidar os tokens antigos!

### **Passo 4: Copiar Novos Tokens**
Após renovar, você receberá:
- **Novo Token** (ex: `ABC123DEF456...`)
- **Novo Client Token** (ex: `XYZ789ABC123...`)
- **Instance ID** (permanece o mesmo)

## 📝 **ATUALIZAR TOKENS NO PROJETO**

### **Opção 1: Script Automático**
1. Execute o script de atualização:
```bash
python atualizar_tokens_zapi.py
```

2. Edite o arquivo `atualizar_tokens_zapi.py` e substitua:
```python
NEW_TOKEN = "SEU_NOVO_TOKEN_AQUI"  # ← Coloque o novo token
NEW_CLIENT_TOKEN = "SEU_NOVO_CLIENT_TOKEN_AQUI"  # ← Coloque o novo client token
```

3. Execute novamente:
```bash
python atualizar_tokens_zapi.py
```

### **Opção 2: Atualização Manual**
Substitua os tokens nos seguintes arquivos:

#### **1. configurar_webhooks_zapi_completo.py**
```python
# Linha 12-14
ZAPI_TOKEN = "SEU_NOVO_TOKEN_AQUI"
ZAPI_CLIENT_TOKEN = "SEU_NOVO_CLIENT_TOKEN_AQUI"
```

#### **2. verificar_status_apis.py**
```python
# Linha 12-14
ZAPI_TOKEN = "SEU_NOVO_TOKEN_AQUI"
ZAPI_CLIENT_TOKEN = "SEU_NOVO_CLIENT_TOKEN_AQUI"
```

#### **3. verificar_renovar_tokens_zapi.py**
```python
# Linha 12-14
ZAPI_TOKEN = "SEU_NOVO_TOKEN_AQUI"
ZAPI_CLIENT_TOKEN = "SEU_NOVO_CLIENT_TOKEN_AQUI"
```

## 🧪 **TESTAR NOVOS TOKENS**

### **1. Verificar Status**
```bash
python verificar_renovar_tokens_zapi.py
```

### **2. Testar Envio de Mensagem**
```bash
python verificar_status_apis.py
```

### **3. Reconfigurar Webhooks**
```bash
python configurar_webhooks_zapi_completo.py
```

## ⚠️ **IMPORTANTE - ANTES DE RENOVAR**

### **⚠️ AVISOS CRÍTICOS:**
1. **Tokens antigos serão invalidados** após renovar
2. **Webhooks precisarão ser reconfigurados**
3. **Faça backup dos tokens antigos** (caso precise)
4. **Teste imediatamente** após renovar

### **📋 CHECKLIST ANTES DE RENOVAR:**
- [ ] Tenho acesso ao painel Z-API
- [ ] Sei qual instância renovar
- [ ] Tenho backup dos tokens atuais
- [ ] Estou pronto para reconfigurar webhooks
- [ ] Posso testar imediatamente após renovar

## 🔄 **APÓS RENOVAR OS TOKENS**

### **1. Atualizar Arquivos**
- Substituir tokens em todos os arquivos
- Verificar se não há erros de digitação

### **2. Testar Funcionamento**
- Verificar status da instância
- Testar envio de mensagem
- Verificar webhooks

### **3. Reconfigurar Webhooks**
- Executar script de configuração
- Verificar se todos os 5 webhooks estão ativos

### **4. Teste Final**
- Enviar mensagem real para WhatsApp
- Verificar se resposta automática funciona

## 🚨 **PROBLEMAS COMUNS**

### **Erro 500 após renovar**
- Verificar se tokens foram copiados corretamente
- Verificar se não há espaços extras
- Aguardar alguns minutos e tentar novamente

### **Webhooks não funcionam**
- Reconfigurar todos os webhooks
- Verificar se URLs estão corretas
- Testar endpoints individualmente

### **WhatsApp desconectado**
- Reconectar WhatsApp no painel Z-API
- Verificar se o celular está conectado
- Escanear QR code novamente se necessário

## 📞 **SUPORTE**

### **Se precisar de ajuda:**
1. **Documentação Z-API**: https://developer.z-api.io/
2. **Painel de Suporte**: https://app.z-api.io/support
3. **Email**: suporte@z-api.io

### **Informações para suporte:**
- Instance ID: `3E4F7360B552F0C2DBCB9E6774402775`
- Erro: `java.lang.NullPointerException`
- Status: Tokens precisam ser renovados

## 🎯 **RESUMO RÁPIDO**

### **O que fazer agora:**
1. **Acessar**: https://app.z-api.io/
2. **Renovar tokens** na instância
3. **Copiar novos tokens**
4. **Atualizar arquivos** do projeto
5. **Testar funcionamento**
6. **Reconfigurar webhooks**

### **Tempo estimado**: 10-15 minutos

**🎉 Após renovar os tokens, seu chatbot estará 100% operacional!** 