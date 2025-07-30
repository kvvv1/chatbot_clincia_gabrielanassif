import { useState, useEffect } from 'react';
import { getConversations } from '../services/api';

export function useConversations(filters) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const data = await getConversations(filters);
      setConversations(data);
      setError(null);
    } catch (err) {
      setError(err.message);
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
    refetch: fetchConversations
  };
} 