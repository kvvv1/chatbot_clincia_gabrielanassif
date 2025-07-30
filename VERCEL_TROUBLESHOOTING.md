# Vercel Deployment Troubleshooting Guide

## Problema: FUNCTION_INVOCATION_FAILED (500 Internal Server Error)

### 1. Verificar Logs do Vercel

Primeiro, acesse os logs do Vercel:
1. Vá para o [Dashboard do Vercel](https://vercel.com/dashboard)
2. Selecione seu projeto
3. Clique em "Functions" na aba lateral
4. Clique na função que está falhando
5. Verifique os logs de erro

### 2. Possíveis Causas e Soluções

#### A. Variáveis de Ambiente Não Configuradas

**Sintoma:** Erro relacionado a `SUPABASE_URL` ou `SUPABASE_ANON_KEY`

**Solução:**
1. No Dashboard do Vercel, vá em "Settings" > "Environment Variables"
2. Adicione as seguintes variáveis:
   ```
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_ANON_KEY=sua_chave_anonima_do_supabase
   SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role_do_supabase
   ```

#### B. Timeout da Função

**Sintoma:** Função falha após 30 segundos

**Solução:**
- O `vercel.json` já foi atualizado para 60 segundos
- Verifique se não há loops infinitos no código

#### C. Memória Insuficiente

**Sintoma:** Erro de memória ou função muito lenta

**Solução:**
- O `vercel.json` já foi atualizado para 2048MB
- Otimize imports e evite carregar módulos desnecessários

#### D. WebSocket em Ambiente Serverless

**Sintoma:** Erro relacionado a WebSocket

**Solução:**
- WebSocket foi desabilitado automaticamente no Vercel
- Use polling ou Server-Sent Events como alternativa

### 3. Testes de Diagnóstico

#### A. Teste Básico de Conectividade

```bash
curl https://chatbot-nassif.vercel.app/
```

#### B. Teste de Health Check

```bash
curl https://chatbot-nassif.vercel.app/health
```

#### C. Teste de Debug (apenas em desenvolvimento)

```bash
curl https://chatbot-nassif.vercel.app/debug
```

#### D. Teste do Dashboard

```bash
curl https://chatbot-nassif.vercel.app/dashboard/status
```

### 4. Script de Teste Automatizado

Execute o script de teste:

```bash
python test_vercel_deployment.py
```

### 5. Verificações de Configuração

#### A. requirements-vercel.txt

Certifique-se de que todas as dependências estão listadas:

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

#### B. vercel.json

Verifique se o arquivo está correto:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python",
      "config": {
        "requirements": "requirements-vercel.txt"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ],
  "env": {
    "PYTHONPATH": ".",
    "VERCEL": "1"
  },
  "functions": {
    "app/main.py": {
      "maxDuration": 60,
      "memory": 2048
    }
  },
  "regions": ["gru1"]
}
```

### 6. Soluções Específicas

#### A. Se o erro persistir após configuração das variáveis:

1. **Redeploy:** Force um novo deploy no Vercel
2. **Clear Cache:** Limpe o cache do Vercel
3. **Check Build Logs:** Verifique se o build está passando

#### B. Se houver erro de importação:

1. Verifique se todos os arquivos `__init__.py` existem
2. Certifique-se de que o `PYTHONPATH` está configurado
3. Verifique se não há imports circulares

#### C. Se houver erro de banco de dados:

1. Verifique se o Supabase está acessível
2. Teste a conexão com o Supabase localmente
3. Verifique se as credenciais estão corretas

### 7. Logs Úteis para Debug

#### A. Logs de Startup

Procure por estas mensagens nos logs:
```
Starting up FastAPI application...
Environment: Vercel
Configuration status: {...}
Routers carregados com sucesso
```

#### B. Logs de Erro

Procure por estas mensagens de erro:
```
Erro ao carregar routers
Erro no endpoint root
Erro no health check
```

### 8. Contatos e Recursos

- **Vercel Support:** https://vercel.com/support
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Supabase Documentation:** https://supabase.com/docs

### 9. Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] requirements-vercel.txt atualizado
- [ ] vercel.json configurado
- [ ] Build passando
- [ ] Testes locais funcionando
- [ ] Logs sem erros críticos
- [ ] Endpoints respondendo corretamente

### 10. Comandos Úteis

```bash
# Testar localmente
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Verificar variáveis de ambiente
python -c "import os; print([k for k in os.environ.keys() if 'SUPABASE' in k])"

# Testar deployment
python test_vercel_deployment.py
``` 