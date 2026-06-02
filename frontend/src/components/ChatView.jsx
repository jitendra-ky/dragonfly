import { useState, useEffect, useRef, useMemo } from 'react';
import useAuthStore from '../store/authStore';
import useChatStore from '../store/chatStore';
import { chatService } from '../services';
import Avatar from './Avatar';
import MessageInput from './MessageInput';
import LoadingSpinner from './LoadingSpinner';

function ChatView() {
  const user = useAuthStore((state) => state.user);
  const { selectedContactId, contacts, messages, setMessages } = useChatStore();
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const selectedContact = contacts.find((c) => c.id === selectedContactId);
  const currentMessages = useMemo(() => messages[selectedContactId] || [], [messages, selectedContactId]);

  // Fetch messages when contact is selected
  useEffect(() => {
    const fetchMessages = async () => {
      if (!selectedContactId) return;

      setLoading(true);
      try {
        const fetchedMessages = await chatService.getMessages(selectedContactId);
        // Ensure each message has proper structure
        const normalizedMessages = fetchedMessages.map(msg => ({
          ...msg,
          sender_id: msg.sender_id || msg.sender || msg.user_id,
          receiver_id: msg.receiver_id || msg.receiver,
          content: msg.content || msg.message,
          timestamp: msg.timestamp || msg.created_at || new Date().toISOString()
        }));
        setMessages(selectedContactId, normalizedMessages);
      } catch (error) {
        console.error('Error fetching messages:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMessages();
  }, [selectedContactId, setMessages]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentMessages]);

  // Format timestamp
  const formatMessageTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  };

  // Group messages by date
  const groupMessagesByDate = (messages) => {
    const groups = {};
    messages.forEach((msg) => {
      const date = new Date(msg.timestamp).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(msg);
    });
    return groups;
  };

  const messageGroups = useMemo(() => groupMessagesByDate(currentMessages), [currentMessages]);

  if (!selectedContact) {
    return null;
  }

  return (
    <div className="flex-1 flex flex-col bg-white h-full">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200 flex items-center flex-shrink-0">
        <Avatar 
          name={selectedContact.full_name || selectedContact.contact || selectedContact.email || 'Unknown'} 
          size="md" 
        />
        <div className="ml-3">
          <p className="text-sm font-medium text-gray-900">
            {selectedContact.full_name || selectedContact.contact || selectedContact.email || 'Unknown Contact'}
          </p>
          <p className="text-xs text-gray-500">
            {selectedContact.email || 'No email available'}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 scrollbar-thin bg-gray-50 min-h-0">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <LoadingSpinner size="lg" />
          </div>
        ) : currentMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500 text-sm">No messages yet. Start the conversation!</p>
          </div>
        ) : (
          <div>
            {Object.entries(messageGroups).map(([date, msgs]) => (
              <div key={date}>
                {/* Date Divider */}
                <div className="flex items-center justify-center my-4">
                  <span className="px-3 py-1 bg-gray-200 text-gray-600 text-xs rounded-full">
                    {date}
                  </span>
                </div>

                {/* Messages */}
                {msgs.map((message, index) => {
                  // More robust sender ID comparison
                  const messageSenderId = message.sender_id || message.sender || message.user_id;
                  const currentUserId = user?.id || user?.user_id;
                  const isSentByMe = String(messageSenderId) === String(currentUserId);
                  
                  // Temporary debug to understand the data structure
                  if (index === 0) {
                    console.log('Sample message structure:', { message, user, messageSenderId, currentUserId, isSentByMe });
                  }

                  return (
                    <div
                      key={`${message.id || index}-${message.timestamp}`}
                      className={`flex mb-4 ${isSentByMe ? 'justify-end' : 'justify-start'}`}
                    >
                      {/* Avatar for received messages (left side) */}
                      {!isSentByMe && (
                        <Avatar
                          name={selectedContact.full_name}
                          size="sm"
                          className="mr-3 flex-shrink-0 self-end"
                        />
                      )}

                      {/* Message content */}
                      <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isSentByMe ? 'order-2' : 'order-1'}`}>
                        <div
                          className={`px-4 py-2 rounded-2xl ${
                            isSentByMe
                              ? 'bg-blue-500 text-white rounded-br-md'
                              : 'bg-white border border-gray-200 text-gray-900 rounded-bl-md'
                          }`}
                        >
                          <p className="text-sm break-words">{message.content}</p>
                        </div>
                        <span
                          className={`text-xs text-gray-500 mt-1 block ${
                            isSentByMe ? 'text-right' : 'text-left'
                          }`}
                        >
                          {formatMessageTime(message.timestamp)}
                        </span>
                      </div>

                      {/* Avatar for sent messages (right side) */}
                      {isSentByMe && (
                        <Avatar
                          name={user?.full_name || user?.name}
                          size="sm"
                          className="ml-3 flex-shrink-0 self-end order-3"
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Message Input */}
      <div className="flex-shrink-0">
        <MessageInput />
      </div>
    </div>
  );
}

export default ChatView;
