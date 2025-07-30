import { useState, useEffect } from 'react';
import { getConversations } from '../services/api';

export function useConversations(filters) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState(null);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const data = await getConversations(filters);
      
      // A nova API retorna { conversations: [], pagination: {} }
      if (data.conversations) {
        setConversations(data.conversations);
        setPagination(data.pagination);
      } else {
        // Fallback para compatibilidade
        setConversations(data);
        setPagination(null);
      }
      
      setError(null);
    } catch (err) {
      console.error('Erro ao buscar conversas:', err);
      setError(err.message);
      setConversations([]);
      setPagination(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, [filters]);

  return {
    conversations,
    loading,
    error,
    pagination,
    refetch: fetchConversations
  };
} 