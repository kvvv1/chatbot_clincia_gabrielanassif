# 🔧 Guia de Solução de Problemas - Vercel

## Problema: Serverless Function Crash (500: INTERNAL_SERVER_ERROR)

### 🔍 Diagnóstico

O erro `FUNCTION_INVOCATION_FAILED` indica que a função serverless no Vercel está falhando durante a execução. Vamos resolver isso passo a passo.

### ✅ Soluções Implementadas

#### 1. **Melhor Tratamento de Erros**
- Adicionado middleware global para capturar exceções
- Logging detalhado para diagnóstico
- Tratamento graceful de configurações ausentes

#### 2. **Configuração Robusta para Serverless**
- Verificação de ambiente Vercel
- Limitação de conexões WebSocket em serverless
- Timeout e memory configurados adequadamente

#### 3. **Supabase em Modo Mock**
- Serviço funciona mesmo sem configuração do Supabase
- Dados simulados para desenvolvimento/teste
- Logs informativos sobre modo mock

### 🚀 Passos para Resolver

#### Passo 1: Verificar Variáveis de Ambiente

No painel do Vercel, configure as seguintes variáveis:

```bash
# Obrigatórias (para funcionamento básico)
SUPABASE_URL=sua_url_do_supabase
SUPABASE_ANON_KEY=sua_chave_anonima_do_supabase
SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role_do_supabase

# Opcionais (para funcionalidades completas)
ZAPI_INSTANCE_ID=seu_instance_id_do_zapi
ZAPI_TOKEN=seu_token_do_zapi
GESTAODS_TOKEN=seu_token_do_gestaods

# Configurações da aplicação
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=*
```

#### Passo 2: Testar a Implantação

Execute o script de teste:

```bash
python test_vercel_deployment.py
```

#### Passo 3: Verificar Logs

No painel do Vercel:
1. Vá para "Functions"
2. Clique na função que está falhando
3. Verifique os logs para identificar o erro específico

### 🔧 Configurações Específicas

#### Vercel Configuration (`vercel.json`)
```json
{
  "functions": {
    "app/main.py": {
      "maxDuration": 30,
      "memory": 1024
    }
  },
  "regions": ["gru1"]
}
```

#### Requirements (`requirements-vercel.txt`)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
httpx==0.25.2
python-dotenv==1.0.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
asyncpg==0.29.0
psycopg2-binary==2.9.9
python-multipart==0.0.6
```

### 🐛 Problemas Comuns e Soluções

#### 1. **Erro de Importação**
```
ModuleNotFoundError: No module named 'app'
```
**Solução**: Verificar se `PYTHONPATH=.` está configurado no `vercel.json`

#### 2. **Timeout da Função**
```
Function invocation failed due to timeout
```
**Solução**: Aumentar `maxDuration` no `vercel.json` (máximo 30s)

#### 3. **Erro de Memória**
```
Function invocation failed due to memory limit
```
**Solução**: Aumentar `memory` no `vercel.json` (máximo 3008MB)

#### 4. **Erro de Conexão com Banco**
```
Connection refused to database
```
**Solução**: Verificar se as variáveis de ambiente do Supabase estão configuradas

#### 5. **Erro de CORS**
```
CORS policy violation
```
**Solução**: Verificar se `CORS_ORIGINS` está configurado corretamente

### 📊 Monitoramento

#### Endpoints de Saúde
- `GET /` - Status básico
- `GET /health` - Verificação detalhada
- `GET /test` - Teste simples
- `GET /dashboard/test` - Teste do dashboard

#### Logs Importantes
```python
# Verificar se estas mensagens aparecem nos logs:
"Routers carregados com sucesso"
"Modo mock ativo - retornando sucesso simulado"
"WebSocket conectado"
```

### 🔄 Deploy e Teste

#### 1. Fazer Deploy
```bash
vercel --prod
```

#### 2. Testar Endpoints
```bash
curl https://seu-app.vercel.app/
curl https://seu-app.vercel.app/health
curl https://seu-app.vercel.app/dashboard/test
```

#### 3. Verificar Logs
```bash
vercel logs
```

### 🆘 Se o Problema Persistir

1. **Verificar Logs Detalhados**
   - Acesse o painel do Vercel
   - Vá para "Functions" > "View Function Logs"
   - Procure por erros específicos

2. **Testar Localmente**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Verificar Dependências**
   ```bash
   pip install -r requirements-vercel.txt
   ```

4. **Contatar Suporte**
   - Se o problema persistir, forneça os logs completos
   - Inclua o ID do erro: `gru1::lksc8-1753877580292-027cbf54088d`

### 📞 Suporte

Para problemas específicos:
1. Execute `python test_vercel_deployment.py`
2. Compartilhe os logs do Vercel
3. Inclua o ID do erro
4. Descreva os passos que levam ao erro

### ✅ Checklist de Verificação

- [ ] Variáveis de ambiente configuradas no Vercel
- [ ] `vercel.json` atualizado
- [ ] `requirements-vercel.txt` atualizado
- [ ] Deploy realizado com sucesso
- [ ] Endpoints de teste funcionando
- [ ] Logs sem erros críticos
- [ ] WebSocket funcionando (se necessário)
- [ ] Conexão com Supabase estabelecida 