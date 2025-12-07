import { useState, useEffect } from 'react';
import useChatStore from '../store/chatStore';
import api from '../utils/axios';
import Modal from './Modal';
import Avatar from './Avatar';
import LoadingSpinner from './LoadingSpinner';

function NewMessageModal({ isOpen, onClose }) {
  const [users, setUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const { contacts, setSelectedContact, setContacts } = useChatStore();

  useEffect(() => {
    if (isOpen) {
      fetchUsers();
    }
  }, [isOpen]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter users based on search and exclude existing contacts
  const filteredUsers = users.filter((user) => {
    const matchesSearch = user.full_name
      .toLowerCase()
      .includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase());
    
    const isNotContact = !contacts.some((contact) => contact.id === user.id);
    
    return matchesSearch && isNotContact;
  });

  const handleSelectUser = (user) => {
    // Add to contacts if not already there
    if (!contacts.some((c) => c.id === user.id)) {
      setContacts([...contacts, user]);
    }
    
    // Select the contact
    setSelectedContact(user.id);
    
    // Close modal
    onClose();
    setSearchQuery('');
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="New Message">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search users by name or email..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          autoFocus
        />
      </div>

      <div className="max-h-96 overflow-y-auto scrollbar-thin">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner size="md" />
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-sm">
            {searchQuery
              ? 'No users found'
              : 'No new users available'}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredUsers.map((user) => (
              <button
                key={user.id}
                onClick={() => handleSelectUser(user)}
                className="w-full p-3 flex items-center hover:bg-gray-50 rounded-lg transition-colors"
              >
                <Avatar name={user.full_name} size="md" className="flex-shrink-0" />
                <div className="ml-3 flex-1 min-w-0 text-left">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {user.full_name}
                  </p>
                  <p className="text-xs text-gray-500 truncate">{user.email}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </Modal>
  );
}

export default NewMessageModal;
