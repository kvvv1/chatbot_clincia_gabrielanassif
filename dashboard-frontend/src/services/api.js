import axios from 'axios';

// Configuração para produção vs desenvolvimento
const isDevelopment = process.env.NODE_ENV === 'development';
const API_BASE_URL = isDevelopment ? '/dashboard' : process.env.REACT_APP_API_URL || 'https://seu-backend.vercel.app/dashboard';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para tratar erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Erro na API:', error);
    throw new Error(error.response?.data?.detail || 'Erro na comunicação com o servidor');
  }
);

export const getConversations = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.status) params.append('status', filters.status);
  if (filters.priority !== null && filters.priority !== undefined) params.append('priority', filters.priority);
  if (filters.search) params.append('search', filters.search);
  if (filters.date_from) params.append('date_from', filters.date_from);
  if (filters.date_to) params.append('date_to', filters.date_to);

  const response = await api.get(`/conversations?${params.toString()}`);
  return response.data;
};

export const getConversationDetail = async (conversationId) => {
  const response = await api.get(`/conversations/${conversationId}`);
  return response.data;
};

export const updateConversation = async (conversationId, updates) => {
  const response = await api.patch(`/conversations/${conversationId}`, updates);
  return response.data;
};

export const addNote = async (conversationId, note, createdBy) => {
  const response = await api.post(`/conversations/${conversationId}/notes`, {
    note,
    created_by: createdBy
  });
  return response.data;
};

export const getAnalytics = async (dateFrom, dateTo) => {
  const params = new URLSearchParams();
  if (dateFrom) params.append('date_from', dateFrom);
  if (dateTo) params.append('date_to', dateTo);

  const response = await api.get(`/analytics/summary?${params.toString()}`);
  return response.data;
}; 