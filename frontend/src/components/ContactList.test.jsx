import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ContactList from './ContactList';

const setSelectedContact = vi.fn();
let chatState = {
  contacts: [],
  selectedContactId: null,
  setSelectedContact,
  messages: {},
};

vi.mock('../store/chatStore', () => ({
  default: (selector) => (selector ? selector(chatState) : chatState),
}));

describe('ContactList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    chatState = {
      contacts: [],
      selectedContactId: null,
      setSelectedContact,
      messages: {},
    };
  });

  it('shows empty state without contacts', () => {
    render(<ContactList />);
    expect(screen.getByText('No contacts yet')).toBeInTheDocument();
  });

  it('filters contacts by search query', async () => {
    const user = userEvent.setup();
    chatState.contacts = [
      { id: 1, email: 'alice@example.com', full_name: 'Alice Doe' },
      { id: 2, email: 'bob@example.com', full_name: 'Bob Doe' },
    ];

    render(<ContactList />);
    await user.type(screen.getByPlaceholderText('Search contacts...'), 'alice');

    expect(screen.getByText('alice@example.com')).toBeInTheDocument();
    expect(screen.queryByText('bob@example.com')).not.toBeInTheDocument();
  });

  it('selects contact when clicked and renders last message', async () => {
    const user = userEvent.setup();
    chatState.contacts = [{ id: 5, email: 'contact@example.com', full_name: 'Contact Name' }];
    chatState.messages = {
      5: [{ id: 1, content: 'Latest message', timestamp: new Date().toISOString() }],
    };

    render(<ContactList />);

    expect(screen.getByText('Latest message')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /contact@example.com/i }));
    expect(setSelectedContact).toHaveBeenCalledWith(5);
  });
});
