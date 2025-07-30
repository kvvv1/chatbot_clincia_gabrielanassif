# 🎛️ Painel de Controle - Frontend

## 📋 Descrição

Frontend React para o painel de controle da secretaria do chatbot clínica. Permite visualizar, gerenciar e analisar conversas em tempo real.

## 🚀 Instalação

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm start
```

## 🏗️ Estrutura

```
src/
├── components/          # Componentes React
│   ├── Header.jsx      # Cabeçalho da aplicação
│   ├── ConversationList.jsx  # Lista de conversas
│   ├── ConversationDetail.jsx # Detalhes da conversa
│   ├── StatusBadge.jsx # Badge de status
│   └── Analytics.jsx   # Componente de análises
├── hooks/              # Hooks personalizados
│   ├── useConversations.js # Hook para conversas
│   └── useWebSocket.js # Hook para WebSocket
├── services/           # Serviços de API
│   └── api.js         # Cliente da API
├── App.jsx            # Componente principal
└── index.js           # Ponto de entrada
```

## 🔧 Funcionalidades

### 📱 Interface Principal
- **Lista de Conversas**: Visualização de todas as conversas com filtros
- **Detalhes da Conversa**: Visualização completa de mensagens e notas
- **Análises**: Métricas e gráficos de performance

### 🎯 Recursos
- **Filtros**: Por status, prioridade e busca por texto
- **Tempo Real**: Atualizações via WebSocket
- **Classificação Inteligente**: Tags automáticas baseadas em IA
- **Notas**: Sistema de anotações para secretaria
- **Métricas**: Analytics em tempo real

### 🎨 Design
- **Responsivo**: Funciona em desktop e mobile
- **Moderno**: Interface limpa com Tailwind CSS
- **Acessível**: Componentes acessíveis e intuitivos

## 🔌 Integração

O frontend se conecta ao backend FastAPI através de:
- **REST API**: Para operações CRUD
- **WebSocket**: Para atualizações em tempo real

## 📊 Métricas Exibidas

- Total de conversas
- Taxa de resolução do bot
- Tempo médio de resolução
- Distribuição por status
- Conversas que precisam de atenção

## 🛠️ Tecnologias

- **React 18**: Framework principal
- **Tailwind CSS**: Estilização
- **Axios**: Cliente HTTP
- **date-fns**: Manipulação de datas
- **WebSocket**: Comunicação em tempo real 