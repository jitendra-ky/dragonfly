
import { render, screen, waitFor } from '@testing-library/react';
import ChatView from './ChatView';

/* eslint-env jest */
import { vi } from 'vitest';

const { setMessages, mockGetMessages } = vi.hoisted(() => ({
  setMessages: vi.fn(),
  mockGetMessages: vi.fn(),
}));

let authState = { user: { id: 1, full_name: 'Me' } };
let chatState = {
  selectedContactId: null,
  contacts: [],
  messages: {},
  setMessages,
};

vi.mock('../store/authStore', () => ({
  default: (selector) => selector(authState),
}));

vi.mock('../store/chatStore', () => ({
  default: (selector) => (selector ? selector(chatState) : chatState),
}));

vi.mock('../services', () => ({
  chatService: {
    getMessages: mockGetMessages,
  },
}));

vi.mock('./MessageInput', () => ({
  default: () => <div>Message Input</div>,
}));

describe('ChatView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Element.prototype.scrollIntoView = vi.fn();
    authState = { user: { id: 1, full_name: 'Me' } };
    chatState = {
      selectedContactId: null,
      contacts: [],
      messages: {},
      setMessages,
    };
  });

  it('renders nothing when no contact is selected', () => {
    const { container } = render(<ChatView />);
    expect(container).toBeEmptyDOMElement();
  });

  it('loads messages and renders chat header/content', async () => {
    chatState = {
      selectedContactId: 2,
      contacts: [{ id: 2, full_name: 'Alice', email: 'alice@example.com' }],
      messages: {
        2: [{ id: 10, sender_id: 2, receiver_id: 1, content: 'hello', timestamp: new Date().toISOString() }],
      },
      setMessages,
    };
    mockGetMessages.mockResolvedValueOnce([
      { id: 11, sender: 2, receiver: 1, message: 'fetched', created_at: new Date().toISOString() },
    ]);

    render(<ChatView />);

    await waitFor(() => {
      expect(mockGetMessages).toHaveBeenCalledWith(2);
      expect(setMessages).toHaveBeenCalled();
    });

    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('alice@example.com')).toBeInTheDocument();
    expect(screen.getByText('hello')).toBeInTheDocument();
    expect(screen.getByText('Message Input')).toBeInTheDocument();
  });
});
