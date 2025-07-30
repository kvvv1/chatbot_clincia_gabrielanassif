# Netlify Deployment Guide

## 🔧 Problema Identificado
- **Erro:** `pg_config executable not found`
- **Causa:** Netlify tentando instalar dependências Python (PostgreSQL) para o frontend React
- **Solução:** Configurar Netlify para construir apenas o frontend

## ✅ Soluções Implementadas

### 1. **Configuração Netlify Corrigida**

#### `netlify.toml` (raiz)
```toml
[build]
  base = "dashboard-frontend"
  publish = "build"
  command = "npm ci && npm run build"

[build.environment]
  NODE_VERSION = "18"
  NPM_FLAGS = "--legacy-peer-deps"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

#### `.netlifyignore` (raiz)
```
# Exclude all backend files from Netlify deployment
app/
requirements*.txt
vercel.json
docker-compose.yml
Dockerfile
*.py
*.md
.env*
venv/
__pycache__/
*.pyc
tests/
scripts/
pytest.ini
setup.py
start_services.*
test_*.py
deploy_*.py
*_TROUBLESHOOTING.md
*_SETUP.md
*_INSTRUCTIONS.md
CONFIGURACAO_*.md
DEPLOY_*.md
INSTRUCOES_*.md
RESUMO_*.md
SUPABASE_*.md
VERCEL_*.md
```

### 2. **Configuração Frontend**

#### `dashboard-frontend/netlify.toml`
```toml
[build]
  publish = "build"
  command = "npm ci && npm run build"
  base = "."

[build.environment]
  NODE_VERSION = "18"
  NPM_FLAGS = "--legacy-peer-deps"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

#### `dashboard-frontend/.netlifyignore`
```
# Exclude backend files from frontend deployment
../app/
../requirements*.txt
../vercel.json
../docker-compose.yml
../Dockerfile
../*.py
../*.md
../.env*
../venv/
../__pycache__/
../*.pyc
../tests/
../scripts/
../pytest.ini
../setup.py
../start_services.*
```

## 🚀 Passos para Deploy

### 1. **Configuração no Netlify Dashboard**

1. Acesse [Netlify Dashboard](https://app.netlify.com/)
2. Clique em "New site from Git"
3. Conecte seu repositório GitHub
4. Configure as seguintes opções:
   - **Base directory:** `dashboard-frontend`
   - **Build command:** `npm ci && npm run build`
   - **Publish directory:** `build`

### 2. **Variáveis de Ambiente**

No Netlify Dashboard, configure as seguintes variáveis de ambiente:

```
NODE_VERSION=18
NPM_FLAGS=--legacy-peer-deps
REACT_APP_API_URL=https://chatbot-nassif.vercel.app/dashboard
```

### 3. **Deploy Manual**

Se preferir fazer deploy manual:

```bash
# Navegar para o diretório frontend
cd dashboard-frontend

# Instalar dependências
npm ci

# Build do projeto
npm run build

# Fazer deploy (se tiver Netlify CLI)
netlify deploy --prod --dir=build
```

## 🔍 Verificação do Deploy

### 1. **Logs de Build**

Verifique se os logs mostram:
```
✅ Build completed successfully
✅ Deploy completed successfully
```

### 2. **Teste dos Endpoints**

Após o deploy, teste:
- Frontend: `https://seu-site.netlify.app`
- Backend: `https://chatbot-nassif.vercel.app/health`

### 3. **Verificação de Funcionalidade**

1. Acesse o dashboard
2. Verifique se consegue carregar conversas
3. Teste a comunicação com o backend

## 🐛 Troubleshooting

### Problema: "pg_config executable not found"

**Solução:**
1. Verifique se o `.netlifyignore` está correto
2. Confirme que `base = "dashboard-frontend"` está no `netlify.toml`
3. Verifique se não há `requirements.txt` sendo incluído

### Problema: "Build failed"

**Solução:**
1. Verifique se todas as dependências estão no `package.json`
2. Confirme se o Node.js version está correto
3. Verifique os logs de build no Netlify

### Problema: "API connection failed"

**Solução:**
1. Verifique se `REACT_APP_API_URL` está configurado
2. Confirme se o backend está funcionando no Vercel
3. Teste a URL da API diretamente

## 📊 Estrutura do Projeto

```
chatbot/
├── app/                    # Backend (Vercel)
├── dashboard-frontend/     # Frontend (Netlify)
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── netlify.toml
│   └── .netlifyignore
├── requirements.txt        # Backend dependencies
├── vercel.json            # Backend config
├── netlify.toml           # Frontend config (root)
└── .netlifyignore         # Exclude backend files
```

## 🔄 Workflow de Deploy

### Backend (Vercel)
```bash
vercel --prod
```

### Frontend (Netlify)
```bash
# Automatic via Git push
git push origin main

# Manual via CLI
cd dashboard-frontend
npm run build
netlify deploy --prod --dir=build
```

## 📞 Suporte

- **Netlify Support:** https://docs.netlify.com/
- **Build Logs:** Dashboard do Netlify > Site > Deploys
- **Environment Variables:** Dashboard do Netlify > Site > Environment variables

## ✅ Checklist

- [ ] `.netlifyignore` configurado
- [ ] `netlify.toml` com `base = "dashboard-frontend"`
- [ ] Variáveis de ambiente configuradas
- [ ] Backend funcionando no Vercel
- [ ] Frontend buildando corretamente
- [ ] Comunicação entre frontend e backend funcionando 