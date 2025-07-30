import React from 'react';
import StatusBadge from './StatusBadge';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

function ConversationList({ conversations, loading, selectedId, onSelect }) {
  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-gray-200 h-20 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  // Safety check to ensure conversations is an array
  if (!Array.isArray(conversations)) {
    console.error('conversations is not an array:', conversations);
    return (
      <div className="p-4 text-center text-gray-500">
        Erro ao carregar conversas
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        Nenhuma conversa encontrada
      </div>
    );
  }

  const getStateColor = (state) => {
    switch (state) {
      case 'inicio': return 'bg-green-500';
      case 'menu_principal': return 'bg-blue-500';
      case 'aguardando_cpf': return 'bg-yellow-500';
      case 'escolhendo_data': return 'bg-purple-500';
      case 'escolhendo_horario': return 'bg-indigo-500';
      case 'confirmando_agendamento': return 'bg-orange-500';
      case 'visualizando_agendamentos': return 'bg-cyan-500';
      case 'cancelando_consulta': return 'bg-red-500';
      case 'lista_espera': return 'bg-pink-500';
      default: return 'bg-gray-500';
    }
  };

  const getStateText = (state) => {
    switch (state) {
      case 'inicio': return 'Início';
      case 'menu_principal': return 'Menu Principal';
      case 'aguardando_cpf': return 'Aguardando CPF';
      case 'escolhendo_data': return 'Escolhendo Data';
      case 'escolhendo_horario': return 'Escolhendo Horário';
      case 'confirmando_agendamento': return 'Confirmando';
      case 'visualizando_agendamentos': return 'Visualizando';
      case 'cancelando_consulta': return 'Cancelando';
      case 'lista_espera': return 'Lista de Espera';
      default: return state;
    }
  };

  const formatPhone = (phone) => {
    if (!phone) return 'N/A';
    // Formatar telefone brasileiro
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 11) {
      return `(${cleaned.slice(0,2)}) ${cleaned.slice(2,7)}-${cleaned.slice(7)}`;
    }
    return phone;
  };

  return (
    <div>
      {conversations.map((conversation) => (
        <div
          key={conversation.id}
          onClick={() => onSelect(conversation)}
          className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors ${
            selectedId === conversation.id ? 'bg-blue-50' : ''
          }`}
        >
          {/* Header da conversa */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900">
                  {formatPhone(conversation.phone)}
                </h3>
                <span className={`w-2 h-2 rounded-full ${getStateColor(conversation.state)}`} />
              </div>
              <p className="text-sm text-gray-500">
                Estado: {getStateText(conversation.state)}
              </p>
            </div>
            <StatusBadge status={conversation.state} />
          </div>

          {/* Informações da conversa */}
          <div className="text-sm text-gray-600 mb-2">
            <p>Mensagens: {conversation.message_count}</p>
            {conversation.context && Object.keys(conversation.context).length > 0 && (
              <p className="text-xs text-gray-500 mt-1">
                Contexto: {Object.keys(conversation.context).join(', ')}
              </p>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>ID: {conversation.id}</span>
            <span>
              {formatDistanceToNow(new Date(conversation.updated_at), {
                addSuffix: true,
                locale: ptBR
              })}
            </span>
          </div>

          {/* Indicador de atividade recente */}
          {new Date(conversation.updated_at) > new Date(Date.now() - 5 * 60 * 1000) && (
            <div className="mt-2 px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
              🟢 Ativo agora
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default ConversationList; 