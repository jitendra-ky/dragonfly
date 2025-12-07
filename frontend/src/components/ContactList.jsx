import { useState } from 'react';
import useChatStore from '../store/chatStore';
import Avatar from './Avatar';

function ContactList() {
  const { contacts, selectedContactId, setSelectedContact, messages } = useChatStore();
  const [searchQuery, setSearchQuery] = useState('');

  // Filter contacts based on search query
  const filteredContacts = contacts.filter((contact) =>
    contact.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Get last message for a contact
  const getLastMessage = (contactId) => {
    const contactMessages = messages[contactId] || [];
    if (contactMessages.length === 0) return null;
    return contactMessages[contactMessages.length - 1];
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Search */}
      <div className="px-4 pb-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search contacts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <svg
            className="absolute left-3 top-2.5 w-5 h-5 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {/* Contacts List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {filteredContacts.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            {searchQuery ? 'No contacts found' : 'No contacts yet'}
          </div>
        ) : (
          <div>
            {filteredContacts.map((contact) => {
              const lastMessage = getLastMessage(contact.id);
              const isSelected = selectedContactId === contact.id;

              return (
                <button
                  key={contact.id}
                  onClick={() => setSelectedContact(contact.id)}
                  className={`w-full p-4 flex items-center hover:bg-gray-50 transition-colors ${
                    isSelected ? 'bg-primary-50 border-l-4 border-primary-600' : ''
                  }`}
                >
                  <Avatar name={contact.full_name} size="md" className="flex-shrink-0" />
                  
                  <div className="ml-3 flex-1 min-w-0 text-left">
                    <div className="flex items-baseline justify-between">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {contact.full_name}
                      </p>
                      {lastMessage && (
                        <span className="text-xs text-gray-500 ml-2">
                          {formatTime(lastMessage.timestamp)}
                        </span>
                      )}
                    </div>
                    {lastMessage && (
                      <p className="text-sm text-gray-500 truncate">
                        {lastMessage.content}
                      </p>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default ContactList;
