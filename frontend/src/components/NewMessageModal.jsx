import { useState, useEffect } from 'react';
import useChatStore from '../store/chatStore';
import { chatService } from '../services';
import Modal from './Modal';
import Avatar from './Avatar';
import LoadingSpinner from './LoadingSpinner';

function NewMessageModal({ isOpen, onClose }) {
  const [users, setUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { contacts, setSelectedContact, setContacts } = useChatStore();

  useEffect(() => {
    let isMounted = true;
    
    if (isOpen) {
      const loadUsers = async () => {
        setLoading(true);
        setError(null);
        try {
          const users = await chatService.getAllUsers();
          console.log('Fetched users:', users);
          // Only update state if component is still mounted
          if (isMounted) {
            setUsers(Array.isArray(users) ? users : []);
          }
        } catch (error) {
          console.error('Error fetching users:', error);
          if (isMounted) {
            setError('Failed to load users. Please try again.');
            setUsers([]);
          }
        } finally {
          if (isMounted) {
            setLoading(false);
          }
        }
      };
      
      loadUsers();
    }
    
    return () => {
      isMounted = false;
    };
  }, [isOpen]);

  const retryFetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const users = await chatService.getAllUsers();
      console.log('Fetched users:', users);
      setUsers(Array.isArray(users) ? users : []);
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Failed to load users. Please try again.');
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter users based on search and exclude existing contacts
  const filteredUsers = users.filter((user) => {
    // Safety check for user object and required fields
    if (!user || !user.id) return false;
    
    const contact = user.contact || '';
    const email = user.email || '';
    
    const matchesSearch = contact
      .toLowerCase()
      .includes(searchQuery.toLowerCase()) ||
      email.toLowerCase().includes(searchQuery.toLowerCase());
    
    const isNotContact = !contacts.some((contact) => contact.id === user.id);
    
    return matchesSearch && isNotContact;
  });

  const handleSelectUser = (user) => {
    // Safety check
    if (!user || !user.id) {
      console.error('Invalid user object:', user);
      return;
    }

    try {
      // Add to contacts if not already there
      if (!contacts.some((c) => c.id === user.id)) {
        setContacts([...contacts, user]);
      }
      
      // Select the contact
      setSelectedContact(user.id);
      
      // Close modal
      onClose();
      setSearchQuery('');
    } catch (error) {
      console.error('Error selecting user:', error);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="New Message">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search users by contact or email..."
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
        ) : error ? (
          <div className="text-center py-8 text-red-500 text-sm">
            <p>{error}</p>
            <button
              onClick={retryFetchUsers}
              className="mt-2 text-blue-500 hover:text-blue-700 underline"
            >
              Try again
            </button>
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
                <Avatar 
                  name={user.contact || user.email || 'Unknown'} 
                  size="md" 
                  className="flex-shrink-0" 
                />
                <div className="ml-3 flex-1 min-w-0 text-left">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {user.contact || 'No contact info'}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {user.email || 'No email'}
                  </p>
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
