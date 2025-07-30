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

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 3: return 'bg-red-500';
      case 2: return 'bg-orange-500';
      case 1: return 'bg-yellow-500';
      default: return 'bg-green-500';
    }
  };

  const getPriorityText = (priority) => {
    switch (priority) {
      case 3: return 'Urgente';
      case 2: return 'Alta';
      case 1: return 'Média';
      default: return 'Baixa';
    }
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
                  {conversation.patient_name || conversation.phone}
                </h3>
                <span className={`w-2 h-2 rounded-full ${getPriorityColor(conversation.priority)}`} />
              </div>
              <p className="text-sm text-gray-500">{conversation.phone}</p>
            </div>
            <StatusBadge status={conversation.status} />
          </div>

          {/* Resumo da conversa */}
          <p className="text-sm text-gray-600 mb-2 line-clamp-2">
            {conversation.ai_summary}
          </p>

          {/* Tags */}
          <div className="flex flex-wrap gap-1 mb-2">
            {conversation.tags?.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
              >
                {tag}
              </span>
            ))}
            {conversation.tags?.length > 3 && (
              <span className="text-xs text-gray-500">
                +{conversation.tags.length - 3}
              </span>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{conversation.message_count} mensagens</span>
            <span>
              {formatDistanceToNow(new Date(conversation.last_message_at), {
                addSuffix: true,
                locale: ptBR
              })}
            </span>
          </div>

          {/* Indicador de atenção necessária */}
          {conversation.status === 'requires_attention' && (
            <div className="mt-2 px-2 py-1 bg-red-100 text-red-700 text-xs rounded">
              ⚠️ Requer atenção imediata
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default ConversationList; 