import React, { useState, useEffect } from 'react';
import ConversationList from './components/ConversationList';
import ConversationDetail from './components/ConversationDetail';
import Analytics from './components/Analytics';
import Header from './components/Header';
import { useWebSocket } from './hooks/useWebSocket';
import { useConversations } from './hooks/useConversations';

function App() {
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [activeTab, setActiveTab] = useState('conversations');
  const [filters, setFilters] = useState({
    status: null,
    priority: null,
    search: ''
  });

  const { conversations, loading, refetch } = useConversations(filters);
  const { lastMessage, isConnected } = useWebSocket(refetch);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      {/* WebSocket Status Indicator */}
      <div className={`px-4 py-1 text-xs text-center ${
        isConnected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
      }`}>
        {isConnected ? '🟢 Conectado em tempo real' : '🔴 Desconectado - reconectando...'}
        <button 
          onClick={() => {
            console.log('Testando conexão manual...');
            // Forçar nova tentativa de conexão
            window.location.reload();
          }}
          className="ml-2 px-2 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600"
        >
          Reconectar
        </button>
      </div>
      
      <div className="flex h-[calc(100vh-64px)]">
        {/* Sidebar com lista de conversas */}
        <div className="w-96 bg-white border-r overflow-hidden flex flex-col">
          {/* Tabs */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('conversations')}
              className={`flex-1 py-3 px-4 text-sm font-medium ${
                activeTab === 'conversations' 
                  ? 'text-blue-600 border-b-2 border-blue-600' 
                  : 'text-gray-500'
              }`}
            >
              Conversas
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex-1 py-3 px-4 text-sm font-medium ${
                activeTab === 'analytics' 
                  ? 'text-blue-600 border-b-2 border-blue-600' 
                  : 'text-gray-500'
              }`}
            >
              Análise
            </button>
          </div>

          {/* Filtros */}
          <div className="p-4 border-b">
            <input
              type="text"
              placeholder="Buscar por telefone, nome ou CPF..."
              className="w-full px-3 py-2 border rounded-lg"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
            
            <div className="flex gap-2 mt-2">
              <select
                className="flex-1 px-3 py-1 border rounded text-sm"
                value={filters.status || ''}
                onChange={(e) => setFilters({ ...filters, status: e.target.value || null })}
              >
                <option value="">Todos Status</option>
                <option value="pending">Pendente</option>
                <option value="in_progress">Em Atendimento</option>
                <option value="completed">Finalizada</option>
                <option value="requires_attention">Atenção</option>
              </select>
              
              <select
                className="flex-1 px-3 py-1 border rounded text-sm"
                value={filters.priority || ''}
                onChange={(e) => setFilters({ ...filters, priority: e.target.value || null })}
              >
                <option value="">Todas Prioridades</option>
                <option value="3">Urgente</option>
                <option value="2">Alta</option>
                <option value="1">Média</option>
                <option value="0">Baixa</option>
              </select>
            </div>
          </div>

          {/* Conteúdo da tab */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'conversations' ? (
              <ConversationList
                conversations={conversations}
                loading={loading}
                selectedId={selectedConversation?.id}
                onSelect={setSelectedConversation}
              />
            ) : (
              <Analytics />
            )}
          </div>
        </div>

        {/* Área de detalhes */}
        <div className="flex-1">
          {selectedConversation ? (
            <ConversationDetail
              conversation={selectedConversation}
              onUpdate={refetch}
            />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p>Selecione uma conversa para ver detalhes</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App; 