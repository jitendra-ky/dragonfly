import { renderHook, waitFor } from '@testing-library/react';
/* eslint-env jest */
import { vi } from 'vitest';
import useWebSocket from './useWebSocket';
import { STORAGE_KEYS } from '../constants';

const setWsConnection = vi.fn();
const setIsConnected = vi.fn();
const addMessage = vi.fn();

let authState = { user: { id: 1 } };
let chatState = {
  setWsConnection,
  setIsConnected,
  addMessage,
  selectedContactId: null,
};

vi.mock('../store/authStore', () => ({
  default: (selector) => selector(authState),
}));

vi.mock('../store/chatStore', () => ({
  default: () => chatState,
}));

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    authState = { user: { id: 1 } };
    chatState = {
      setWsConnection,
      setIsConnected,
      addMessage,
      selectedContactId: null,
    };
  });

  it('attempts websocket connection when user and token exist', async () => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'access-token');

    const ws = {
      readyState: 1,
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    const wsCtor = vi.fn(() => ws);
    wsCtor.OPEN = 1;
    global.WebSocket = wsCtor;
    window.WebSocket = wsCtor;

    const { result, unmount } = renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(global.WebSocket).toHaveBeenCalled();
    });

    expect(result.current.sendMessage(2, 'outgoing')).toBe(false);

    unmount();
    expect(setIsConnected).toHaveBeenCalledWith(false);
  });

  it('returns false when trying to send before socket is open', () => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'access-token');

    const ws = {
      readyState: 0,
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    const wsCtor = vi.fn(() => ws);
    wsCtor.OPEN = 1;
    global.WebSocket = wsCtor;
    window.WebSocket = wsCtor;

    const { result } = renderHook(() => useWebSocket());
    expect(result.current.sendMessage(2, 'x')).toBe(false);
    expect(ws.send).not.toHaveBeenCalled();
  });
});
