import { useState, useEffect, useRef } from 'react';
import useAuthStore from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import useChatStore from '../store/chatStore';
import useWebSocket from '../hooks/useWebSocket';
import { chatService } from '../services';
import ContactList from './ContactList';
import ChatView from './ChatView';
import NewMessageModal from './NewMessageModal';
import Avatar from './Avatar';

function ChatLayout() {
  const user = useAuthStore((state) => state.user);
  const signOut = useAuthStore((state) => state.signOut);
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showNewMessageModal, setShowNewMessageModal] = useState(false);
  const { contacts, setContacts, selectedContactId } = useChatStore();
  const userMenuRef = useRef(null);

  // Initialize WebSocket
  useWebSocket();

  // Fetch contacts on mount
  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const contacts = await chatService.getContacts();
        setContacts(contacts);
      } catch (error) {
        console.error('Error fetching contacts:', error);
      }
    };

    fetchContacts();
  }, [setContacts]);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    signOut();
    navigate('/signin');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div
        className={`${
          showSidebar ? 'w-80' : 'w-0'
        } lg:w-80 bg-white border-r border-gray-200 flex flex-col transition-all duration-300 overflow-hidden shadow-sm`}
      >
        {/* Sidebar Header */}
        <div className="bg-gray-50 p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {/* Logo/App Name */}
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="lg:hidden p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <h1 className="text-xl font-semibold text-gray-800">Dragonfly</h1>
            </div>
            
            {/* User Profile Menu */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Avatar name={user?.full_name || user?.email} size="sm" />
                <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* User Menu Dropdown */}
              {showUserMenu && (
                <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <div className="flex items-center space-x-3">
                      <Avatar name={user?.full_name || user?.email} size="md" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {user?.full_name || 'User'}
                        </p>
                        <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowNewMessageModal(true)}
                    className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-3"
                  >
                    <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>New Message</span>
                  </button>
                  <hr className="my-1" />
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-3 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-3"
                  >
                    <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Contact List */}
        <div className="flex-1 overflow-hidden">
          <ContactList />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white">
        {/* Mobile Header */}
        <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center shadow-sm">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="mr-3 p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold text-gray-800">Dragonfly</h1>
        </div>

        {/* Chat View */}
        {selectedContactId ? (
          <div className="flex-1 h-full min-h-0">
            <ChatView />
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center max-w-sm mx-auto">
              <div className="w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-12 h-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-medium text-gray-900 mb-2">Welcome to Dragonfly</h3>
              <p className="text-gray-500 mb-6">
                Select a conversation from the sidebar or start a new message to begin chatting.
              </p>
              <button
                onClick={() => setShowNewMessageModal(true)}
                className="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Start New Message
              </button>
            </div>
          </div>
        )}
      </div>

      {/* New Message Modal */}
      <NewMessageModal
        isOpen={showNewMessageModal}
        onClose={() => setShowNewMessageModal(false)}
      />
    </div>
  );
}

export default ChatLayout;