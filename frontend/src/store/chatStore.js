import { create } from 'zustand';

const useChatStore = create((set) => ({
  // State
  contacts: [],
  messages: {}, // { contactId: [messages] }
  selectedContactId: null,
  wsConnection: null,
  isConnected: false,
  loading: false,
  error: null,

  // Actions
  setContacts: (contacts) => set({ contacts }),
  
  setMessages: (contactId, messages) =>
    set((state) => ({
      messages: { ...state.messages, [contactId]: messages },
    })),

  addMessage: (contactId, message) =>
    set((state) => {
      const currentMessages = state.messages[contactId] || [];
      return {
        messages: {
          ...state.messages,
          [contactId]: [...currentMessages, message],
        },
      };
    }),

  setSelectedContact: (contactId) => set({ selectedContactId: contactId }),

  setWsConnection: (connection) => set({ wsConnection: connection }),

  setIsConnected: (isConnected) => set({ isConnected }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  // Clear chat data on logout
  clearChatData: () =>
    set({
      contacts: [],
      messages: {},
      selectedContactId: null,
      wsConnection: null,
      isConnected: false,
    }),
}));

export default useChatStore;
