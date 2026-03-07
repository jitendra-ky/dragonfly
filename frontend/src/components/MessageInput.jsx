import { useState } from 'react';
import useAuthStore from '../store/authStore';
import useChatStore from '../store/chatStore';
import useWebSocket from '../hooks/useWebSocket';
import { chatService } from '../services';
import Button from './Button';

function MessageInput() {
  const user = useAuthStore((state) => state.user);
  const { selectedContactId, addMessage, isConnected } = useChatStore();
  const { sendMessage } = useWebSocket();
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!message.trim() || !selectedContactId) return;

    const messageContent = message.trim();
    setMessage('');
    setSending(true);

    try {
      // Try to send via WebSocket first
      if (isConnected) {
        const sent = sendMessage(selectedContactId, messageContent);
        if (sent) {
          // Message sent via WebSocket, also save to backend
          await chatService.sendMessage(selectedContactId, messageContent);
          setSending(false);
          return;
        }
      }

      // Fallback to HTTP if WebSocket not available
      const response = await chatService.sendMessage(selectedContactId, messageContent);

      // Add message to store manually if WebSocket didn't handle it
      if (!isConnected) {
        // Ensure the message has the correct sender_id
        const messageToAdd = {
          ...response,
          sender_id: user?.id,
          receiver_id: selectedContactId,
          content: messageContent,
          timestamp: response.timestamp || new Date().toISOString()
        };
        addMessage(selectedContactId, messageToAdd);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessage(messageContent); // Restore message on error
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 bg-white">
      <div className="flex items-end space-x-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          rows="1"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
          style={{ maxHeight: '120px' }}
          disabled={sending}
        />
        <Button
          type="submit"
          variant="primary"
          disabled={!message.trim() || sending}
          className="px-6"
        >
          {sending ? (
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </Button>
      </div>
    </form>
  );
}

export default MessageInput;
