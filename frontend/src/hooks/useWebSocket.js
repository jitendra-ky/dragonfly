import { useEffect, useCallback, useRef } from 'react';
import useAuthStore from '../store/authStore';
import useChatStore from '../store/chatStore';
import { STORAGE_KEYS } from '../constants';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/chat';

function useWebSocket() {
  const user = useAuthStore((state) => state.user);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const { setWsConnection, setIsConnected, addMessage, selectedContactId: _selectedContactId } = useChatStore();
  const connectRef = useRef(null);

  const connect = useCallback(() => {
    if (!user) return;

    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    if (!token) return;

    try {
      const ws = new WebSocket(`${WS_URL}?token=${token}`);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setWsConnection(ws);
        wsRef.current = ws;
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const { sender, receiver, content, timestamp } = data;

          // Determine the contact ID (the other person in the conversation)
          const contactId = String(sender) === String(user?.id) ? receiver : sender;

          // Add message to store
          addMessage(contactId, {
            sender_id: String(sender),
            receiver_id: String(receiver),
            content,
            timestamp: timestamp || new Date().toISOString(),
          });
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        wsRef.current = null;

        // Attempt to reconnect with exponential backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          console.log(`Reconnecting in ${delay}ms...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current += 1;
            if (connectRef.current) connectRef.current();
          }, delay);
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
    }
  }, [user, setIsConnected, setWsConnection, addMessage]);

  // keep a ref to the latest connect function to avoid use-before-declare issues
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setWsConnection(null);
  }, [setIsConnected, setWsConnection]);

  const sendMessage = useCallback(
    (receiverId, content) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        const message = {
          sender: String(user?.id),
          receiver: String(receiverId),
          content,
        };
        wsRef.current.send(JSON.stringify(message));
        return true;
      }
      return false;
    },
    [user]
  );

  useEffect(() => {
    if (user) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [user, connect, disconnect]);

  return {
    sendMessage,
    disconnect,
  };
}

export default useWebSocket;
