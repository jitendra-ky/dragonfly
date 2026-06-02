import { vi } from 'vitest'
import useChatStore from './chatStore'

describe('chatStore', () => {
  beforeEach(() => {
    useChatStore.setState({
      contacts: [],
      messages: {},
      selectedContactId: null,
      wsConnection: null,
      isConnected: false,
      loading: false,
      error: null,
    });
  });

  it('sets contacts and selected contact', () => {
    const contacts = [{ id: 1, email: 'a@b.com' }];
    useChatStore.getState().setContacts(contacts);
    useChatStore.getState().setSelectedContact(1);

    expect(useChatStore.getState().contacts).toEqual(contacts);
    expect(useChatStore.getState().selectedContactId).toBe(1);
  });

  it('sets and appends messages', () => {
    useChatStore.getState().setMessages(1, [{ id: 'm1', content: 'first' }]);
    useChatStore.getState().addMessage(1, { id: 'm2', content: 'second' });

    expect(useChatStore.getState().messages[1]).toEqual([
      { id: 'm1', content: 'first' },
      { id: 'm2', content: 'second' },
    ]);
  });

  it('sets flags, websocket connection and clears chat data', () => {
    const ws = { close: vi.fn() };
    useChatStore.getState().setWsConnection(ws);
    useChatStore.getState().setIsConnected(true);
    useChatStore.getState().setLoading(true);
    useChatStore.getState().setError('boom');

    expect(useChatStore.getState().wsConnection).toBe(ws);
    expect(useChatStore.getState().isConnected).toBe(true);
    expect(useChatStore.getState().loading).toBe(true);
    expect(useChatStore.getState().error).toBe('boom');

    useChatStore.getState().clearChatData();
    expect(useChatStore.getState().contacts).toEqual([]);
    expect(useChatStore.getState().messages).toEqual({});
    expect(useChatStore.getState().selectedContactId).toBeNull();
    expect(useChatStore.getState().wsConnection).toBeNull();
    expect(useChatStore.getState().isConnected).toBe(false);
  });
});
