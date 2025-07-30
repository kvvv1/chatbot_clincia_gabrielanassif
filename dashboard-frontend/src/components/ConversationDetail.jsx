import React, { useState, useEffect } from 'react';
import StatusBadge from './StatusBadge';
import { getConversationDetail, updateConversation, addNote } from '../services/api';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

function ConversationDetail({ conversation, onUpdate }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (conversation?.id) {
      loadConversationDetail();
    }
  }, [conversation?.id]);

  const loadConversationDetail = async () => {
    try {
      setLoading(true);
      const data = await getConversationDetail(conversation.id);
      setDetail(data);
    } catch (error) {
      console.error('Erro ao carregar detalhes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      setUpdating(true);
      await updateConversation(conversation.id, { status: newStatus });
      onUpdate();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    } finally {
      setUpdating(false);
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    try {
      await addNote(conversation.id, newNote, 'Secretaria');
      setNewNote('');
      loadConversationDetail();
    } catch (error) {
      console.error('Erro ao adicionar nota:', error);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="p-6 text-center text-gray-500">
        Erro ao carregar detalhes da conversa
      </div>
    );
  }

  const { conversation: conv, messages, notes } = detail;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b bg-white">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {conv.patient_name || conv.phone}
            </h2>
            <p className="text-gray-500">{conv.phone}</p>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge status={conv.status} />
            <select
              className="px-3 py-1 border rounded text-sm"
              value={conv.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              disabled={updating}
            >
              <option value="pending">Pendente</option>
              <option value="in_progress">Em Atendimento</option>
              <option value="completed">Finalizada</option>
              <option value="requires_attention">Atenção</option>
              <option value="spam">Spam</option>
            </select>
          </div>
        </div>

        {/* Informações da conversa */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Prioridade:</span> {conv.priority}
          </div>
          <div>
            <span className="font-medium">Sentimento:</span> {conv.sentiment_score || 0}
          </div>
          <div>
            <span className="font-medium">Mensagens:</span> {conv.message_count}
          </div>
          <div>
            <span className="font-medium">Última mensagem:</span>{' '}
            {format(new Date(conv.last_message_at), 'dd/MM/yyyy HH:mm', { locale: ptBR })}
          </div>
        </div>

        {/* Ação sugerida */}
        {conv.ai_suggested_action && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
            <p className="text-sm font-medium text-blue-800">Ação Sugerida:</p>
            <p className="text-sm text-blue-700">{conv.ai_suggested_action}</p>
          </div>
        )}
      </div>

      {/* Conteúdo */}
      <div className="flex-1 flex">
        {/* Mensagens */}
        <div className="flex-1 p-6 overflow-y-auto">
          <h3 className="text-lg font-medium mb-4">Mensagens</h3>
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    message.sender === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  <p className="text-sm">{message.message}</p>
                  <p className="text-xs opacity-75 mt-1">
                    {format(new Date(message.timestamp), 'HH:mm', { locale: ptBR })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Notas */}
        <div className="w-80 border-l bg-gray-50 p-6">
          <h3 className="text-lg font-medium mb-4">Notas</h3>
          
          {/* Adicionar nota */}
          <div className="mb-4">
            <textarea
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Adicionar nota..."
              className="w-full px-3 py-2 border rounded text-sm resize-none"
              rows="3"
            />
            <button
              onClick={handleAddNote}
              className="mt-2 px-4 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
            >
              Adicionar Nota
            </button>
          </div>

          {/* Lista de notas */}
          <div className="space-y-3">
            {notes.map((note) => (
              <div key={note.id} className="bg-white p-3 rounded border">
                <p className="text-sm text-gray-800">{note.note}</p>
                <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                  <span>{note.created_by}</span>
                  <span>
                    {format(new Date(note.created_at), 'dd/MM HH:mm', { locale: ptBR })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ConversationDetail; 