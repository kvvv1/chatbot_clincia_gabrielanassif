import axios from 'axios';

// Configuração para produção vs desenvolvimento
const isDevelopment = process.env.NODE_ENV === 'development';
const API_BASE_URL = isDevelopment ? 'http://localhost:8000/dashboard' : 'https://chatbot-clincia.vercel.app/dashboard';

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

// Endpoints de conversas
export const getConversations = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.page) params.append('page', filters.page);
  if (filters.limit) params.append('limit', filters.limit);
  if (filters.status) params.append('status', filters.status);
  if (filters.search) params.append('search', filters.search);

  const response = await api.get(`/conversations?${params.toString()}`);
  return response.data;
};

export const getConversationDetail = async (conversationId) => {
  const response = await api.get(`/conversations/${conversationId}`);
  return response.data;
};

export const sendMessageToConversation = async (conversationId, message) => {
  const response = await api.post(`/conversations/${conversationId}/send-message`, {
    message: message
  });
  return response.data;
};

// Endpoints de agendamentos
export const getAppointments = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.page) params.append('page', filters.page);
  if (filters.limit) params.append('limit', filters.limit);
  if (filters.status) params.append('status', filters.status);
  if (filters.date_from) params.append('date_from', filters.date_from);
  if (filters.date_to) params.append('date_to', filters.date_to);

  const response = await api.get(`/appointments?${params.toString()}`);
  return response.data;
};

// Endpoints de analytics
export const getAnalytics = async () => {
  const response = await api.get('/analytics');
  return response.data;
};

// Endpoints de saúde
export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Endpoints de webhook
export const configureWebhook = async () => {
  const response = await api.get('/webhook/configure');
  return response.data;
};

export const getWebhookStatus = async () => {
  const response = await api.get('/webhook/status');
  return response.data;
};

export const testWebhook = async () => {
  const response = await api.get('/webhook/test');
  return response.data;
};

export const testMessage = async () => {
  const response = await api.post('/webhook/test-message');
  return response.data;
}; 