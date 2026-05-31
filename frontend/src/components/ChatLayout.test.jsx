import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import ChatLayout from './ChatLayout';

const { mockNavigate, mockSignOut, mockSetContacts, mockGetContacts } = vi.hoisted(() => ({
  mockNavigate: vi.fn(),
  mockSignOut: vi.fn(),
  mockSetContacts: vi.fn(),
  mockGetContacts: vi.fn(),
}));

let authState = { user: { full_name: 'John', email: 'john@example.com' }, signOut: mockSignOut };
let chatState = {
  contacts: [],
  setContacts: mockSetContacts,
  selectedContactId: null,
};

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../store/authStore', () => ({
  default: (selector) => selector(authState),
}));

vi.mock('../store/chatStore', () => ({
  default: (selector) => (selector ? selector(chatState) : chatState),
}));

vi.mock('../hooks/useWebSocket', () => ({
  default: vi.fn(),
}));

vi.mock('../services', () => ({
  chatService: {
    getContacts: mockGetContacts,
  },
}));

vi.mock('./ContactList', () => ({ default: () => <div>Contact List</div> }));
vi.mock('./ChatView', () => ({ default: () => <div>Chat View</div> }));
vi.mock('./NewMessageModal', () => ({
  default: ({ isOpen }) => (isOpen ? <div>New Message Modal</div> : null),
}));

describe('ChatLayout', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    authState = { user: { full_name: 'John', email: 'john@example.com' }, signOut: mockSignOut };
    chatState = {
      contacts: [],
      setContacts: mockSetContacts,
      selectedContactId: null,
    };
    mockGetContacts.mockResolvedValue([{ id: 1, email: 'a@b.com' }]);
  });

  it('fetches contacts and renders empty-chat welcome state', async () => {
    render(
      <MemoryRouter>
        <ChatLayout />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(mockGetContacts).toHaveBeenCalled();
      expect(mockSetContacts).toHaveBeenCalled();
    });

    expect(screen.getByText('Welcome to Dragonfly')).toBeInTheDocument();
    expect(screen.getByText('Contact List')).toBeInTheDocument();
  });

  it('opens menu and signs out', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <ChatLayout />
      </MemoryRouter>
    );

    await user.click(screen.getAllByRole('button')[1]);
    await user.click(screen.getByRole('button', { name: /sign out/i }));

    expect(mockSignOut).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/signin');
  });
});
