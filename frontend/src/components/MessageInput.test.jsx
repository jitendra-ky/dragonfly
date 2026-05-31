/* eslint-env jest */
import { vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MessageInput from './MessageInput';

const { addMessage, sendMessage, mockSendHttp } = vi.hoisted(() => ({
  addMessage: vi.fn(),
  sendMessage: vi.fn(),
  mockSendHttp: vi.fn(),
}));

let authState = { user: { id: 10 } };
let chatState = {
  selectedContactId: 22,
  addMessage,
  isConnected: true,
};

vi.mock('../store/authStore', () => ({
  default: (selector) => selector(authState),
}));

vi.mock('../store/chatStore', () => ({
  default: (selector) => (selector ? selector(chatState) : chatState),
}));

vi.mock('../hooks/useWebSocket', () => ({
  default: () => ({ sendMessage }),
}));

vi.mock('../services', () => ({
  chatService: {
    sendMessage: mockSendHttp,
  },
}));

describe('MessageInput', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    authState = { user: { id: 10 } };
    chatState = { selectedContactId: 22, addMessage, isConnected: true };
  });

  it('sends via websocket and persists via HTTP', async () => {
    const user = userEvent.setup();
    sendMessage.mockReturnValueOnce(true);
    mockSendHttp.mockResolvedValueOnce({ id: 1, timestamp: new Date().toISOString() });

    render(<MessageInput />);

    const textbox = screen.getByPlaceholderText('Type a message...');
    await user.type(textbox, 'hello');
    await user.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(sendMessage).toHaveBeenCalledWith(22, 'hello');
      expect(mockSendHttp).toHaveBeenCalledWith(22, 'hello');
      expect(addMessage).toHaveBeenCalled();
    });
  });

  it('falls back to HTTP when disconnected', async () => {
    const user = userEvent.setup();
    chatState = { selectedContactId: 22, addMessage, isConnected: false };
    mockSendHttp.mockResolvedValueOnce({ id: 2, timestamp: 'now' });

    render(<MessageInput />);
    await user.type(screen.getByPlaceholderText('Type a message...'), 'fallback');
    await user.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(sendMessage).not.toHaveBeenCalled();
      expect(mockSendHttp).toHaveBeenCalledWith(22, 'fallback');
      expect(addMessage).toHaveBeenCalled();
    });
  });
});
