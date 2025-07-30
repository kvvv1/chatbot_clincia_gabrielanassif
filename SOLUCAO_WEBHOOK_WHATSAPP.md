# Solução para Problema do Webhook WhatsApp

## Problema Identificado

O log mostra um redirecionamento 307:
```
2025-07-30T16:57:51.211Z [info] 127.0.0.1 - - [30/Jul/2025 16:57:51] "POST /webhook/ HTTP/1.1" 200 -
2025-07-30T16:59:29] "POST /webhook HTTP/1.1" 307 -
```

Isso indica que o Z-API está tentando acessar `/webhook` mas está sendo redirecionado para `/webhook/`.

## Soluções Implementadas

### 1. Adicionado Handler para Webhook sem Barra Final

No arquivo `app/handlers/webhook.py`, adicionei um handler adicional:

```python
@router.post("")
async def webhook_handler_no_slash(request: Request):
    """Handler para webhook sem barra final - compatibilidade com Z-API"""
    return await webhook_handler(request)
```

### 2. Melhorado Logging para Debug

Adicionei logs mais detalhados para identificar problemas:

```python
logger.info(f"URL: {request.url}")
logger.info(f"Method: {request.method}")
logger.info(f"Headers: {dict(request.headers)}")
logger.info(f"Body raw: {body}")
```

### 3. Melhorado Tratamento de Erros JSON

Adicionei tratamento específico para erros de parsing JSON:

```python
try:
    data = await request.json()
    logger.info(f"Dados do webhook: {json.dumps(data, indent=2)}")
except Exception as json_error:
    logger.error(f"Erro ao parsear JSON: {str(json_error)}")
    logger.error(f"Body recebido: {body}")
    return {
        "status": "success",
        "message": "Webhook recebido (erro no JSON)",
        "timestamp": datetime.now().isoformat() + "Z"
    }
```

## Passos para Resolver

### 1. Verificar Configuração do Z-API

Execute o script de configuração:

```bash
python configure_webhook.py
```

Certifique-se de que as variáveis de ambiente estão configuradas:
- `ZAPI_INSTANCE_ID`
- `ZAPI_TOKEN`
- `ZAPI_CLIENT_TOKEN`
- `APP_HOST` (URL do seu app no Vercel)

### 2. Testar Endpoint Manualmente

Use o script de teste:

```bash
python test_webhook_detailed.py
```

Substitua a URL base pela sua URL real do Vercel.

### 3. Verificar Logs no Vercel

Após fazer o deploy das alterações, envie uma mensagem para o WhatsApp e verifique os logs no Vercel. Agora você verá logs mais detalhados que ajudarão a identificar o problema.

### 4. Configurar Webhook no Z-API

Se o webhook não estiver configurado corretamente, use o endpoint de configuração:

```
GET https://seu-app.vercel.app/webhook/configure
```

## Verificações Importantes

### 1. URL do Webhook
Certifique-se de que a URL configurada no Z-API é exatamente:
```
https://seu-app.vercel.app/webhook
```

### 2. Variáveis de Ambiente
Verifique se todas as variáveis estão configuradas no Vercel:
- Z-API credentials
- Supabase credentials
- APP_HOST

### 3. Status da Instância Z-API
Verifique se a instância do Z-API está conectada e funcionando.

## Teste Completo

1. **Deploy das alterações** no Vercel
2. **Configurar webhook** usando o script
3. **Testar endpoint** manualmente
4. **Enviar mensagem** para o WhatsApp
5. **Verificar logs** no Vercel
6. **Verificar resposta** no WhatsApp

## Logs Esperados

Com as melhorias, você deve ver logs como:

```
2025-07-30T16:57:51.210Z [info] Webhook recebido do Z-API
2025-07-30T16:57:51.210Z [info] URL: https://seu-app.vercel.app/webhook
2025-07-30T16:57:51.210Z [info] Method: POST
2025-07-30T16:57:51.210Z [info] Headers: {...}
2025-07-30T16:57:51.210Z [info] Body raw: {...}
2025-07-30T16:57:51.210Z [info] Dados do webhook: {...}
2025-07-30T16:57:51.210Z [info] Processando evento de mensagem...
2025-07-30T16:57:51.210Z [info] Webhook processado com sucesso
```

## Se o Problema Persistir

1. **Verifique a URL exata** que o Z-API está enviando
2. **Teste com curl** para simular o webhook
3. **Verifique se há CORS** interferindo
4. **Confirme que a instância Z-API** está conectada
5. **Verifique os logs completos** no Vercel

## Comandos Úteis

```bash
# Testar webhook
curl -X POST https://seu-app.vercel.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"message","data":{"id":"test","type":"text","from":"553198600366@c.us","fromMe":false,"text":{"body":"teste"}}}'

# Verificar status
curl https://seu-app.vercel.app/webhook/

# Configurar webhook
curl https://seu-app.vercel.app/webhook/configure
``` 