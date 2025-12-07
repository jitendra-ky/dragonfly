import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import useChatStore from '../store/chatStore';
import api from '../utils/axios';
import Avatar from './Avatar';
import MessageInput from './MessageInput';
import LoadingSpinner from './LoadingSpinner';

function ChatView() {
  const { user } = useAuth();
  const { selectedContactId, contacts, messages, setMessages } = useChatStore();
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const selectedContact = contacts.find((c) => c.id === selectedContactId);
  const currentMessages = messages[selectedContactId] || [];

  // Fetch messages when contact is selected
  useEffect(() => {
    const fetchMessages = async () => {
      if (!selectedContactId) return;

      setLoading(true);
      try {
        const response = await api.get(`/api/messages/?other_user_id=${selectedContactId}`);
        setMessages(selectedContactId, response.data);
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

  const messageGroups = groupMessagesByDate(currentMessages);

  if (!selectedContact) {
    return null;
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200 flex items-center">
        <Avatar name={selectedContact.full_name} size="md" />
        <div className="ml-3">
          <p className="text-sm font-medium text-gray-900">{selectedContact.full_name}</p>
          <p className="text-xs text-gray-500">{selectedContact.email}</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 scrollbar-thin bg-gray-50">
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
                  const isSentByMe = message.sender_id === user.id;

                  return (
                    <div
                      key={index}
                      className={`flex mb-4 ${isSentByMe ? 'justify-end' : 'justify-start'}`}
                    >
                      {!isSentByMe && (
                        <Avatar
                          name={selectedContact.full_name}
                          size="sm"
                          className="mr-2 flex-shrink-0"
                        />
                      )}

                      <div className={`max-w-xs lg:max-w-md ${isSentByMe ? 'order-1' : ''}`}>
                        <div
                          className={`px-4 py-2 rounded-lg ${
                            isSentByMe
                              ? 'bg-primary-600 text-white'
                              : 'bg-white border border-gray-200 text-gray-900'
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

                      {isSentByMe && (
                        <Avatar
                          name={user.full_name}
                          size="sm"
                          className="ml-2 flex-shrink-0"
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
      <MessageInput />
    </div>
  );
}

export default ChatView;
