import { useState, useEffect, useRef } from 'react';

export function useWebSocket(onMessage) {
  const [lastMessage, setLastMessage] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    console.log('🚀 Iniciando WebSocket...');
    
    // Delay inicial para dar tempo do backend inicializar
    const initialDelay = setTimeout(() => {
      // Conectar diretamente na porta 8000 (backend)
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = '127.0.0.1'; // Usar IP explícito para evitar problemas de DNS
      const port = '8000';
      const wsUrl = `${protocol}//${host}:${port}/dashboard/ws`;
      
      console.log('Tentando conectar WebSocket:', wsUrl);
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('✅ WebSocket conectado com sucesso');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 Mensagem WebSocket recebida:', data);
          setLastMessage(data);
          if (onMessage) {
            onMessage(data);
          }
        } catch (error) {
          console.error('❌ Erro ao processar mensagem WebSocket:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket desconectado', { code: event.code, reason: event.reason, wasClean: event.wasClean });
        setIsConnected(false);
      };

      ws.onerror = (error) => {
        console.error('❌ Erro no WebSocket:', error);
        setIsConnected(false);
      };

      wsRef.current = ws;
    }, 3000);

    return () => {
      console.log('🧹 Limpando WebSocket...');
      clearTimeout(initialDelay);
      
      // Fechar conexão WebSocket
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
        wsRef.current = null;
      }
    };
  }, [onMessage]);

  return { lastMessage, isConnected };
} 