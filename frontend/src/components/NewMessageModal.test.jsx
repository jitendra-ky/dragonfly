import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import NewMessageModal from './NewMessageModal';

const { setSelectedContact, setContacts, mockGetAllUsers } = vi.hoisted(() => ({
  setSelectedContact: vi.fn(),
  setContacts: vi.fn(),
  mockGetAllUsers: vi.fn(),
}));

let chatState = {
  contacts: [],
  setSelectedContact,
  setContacts,
};

vi.mock('../store/chatStore', () => ({
  default: (selector) => (selector ? selector(chatState) : chatState),
}));

vi.mock('../services', () => ({
  chatService: {
    getAllUsers: mockGetAllUsers,
  },
}));

describe('NewMessageModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    chatState = { contacts: [], setSelectedContact, setContacts };
  });

  it('loads users and selects one', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    mockGetAllUsers.mockResolvedValueOnce([
      { id: 5, contact: 'Alice', email: 'alice@example.com' },
      { id: 6, contact: 'Bob', email: 'bob@example.com' },
    ]);

    render(<NewMessageModal isOpen onClose={onClose} />);

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /alice/i }));

    expect(setContacts).toHaveBeenCalled();
    expect(setSelectedContact).toHaveBeenCalledWith(5);
    expect(onClose).toHaveBeenCalled();
  });

  it('shows retry flow on fetch error', async () => {
    const user = userEvent.setup();
    mockGetAllUsers.mockRejectedValueOnce(new Error('network'));
    mockGetAllUsers.mockResolvedValueOnce([{ id: 7, contact: 'Retry User', email: 'retry@example.com' }]);

    render(<NewMessageModal isOpen onClose={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load users. Please try again.')).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /try again/i }));

    await waitFor(() => {
      expect(screen.getByText('Retry User')).toBeInTheDocument();
    });
  });
});
