import { API_CONFIG } from '../constants';

const mockApi = {
  get: vi.fn(),
  post: vi.fn(),
};

vi.mock('./api', () => ({
  default: mockApi,
}));

describe('chatService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('gets contacts', async () => {
    const contacts = [{ id: 1, email: 'a@b.com' }];
    mockApi.get.mockResolvedValueOnce({ data: contacts });

    const { chatService } = await import('./chatService');
    const result = await chatService.getContacts();

    expect(mockApi.get).toHaveBeenCalledWith(API_CONFIG.ENDPOINTS.CONTACTS);
    expect(result).toEqual(contacts);
  });

  it('gets messages with receiver header', async () => {
    const messages = [{ id: 1, content: 'hello' }];
    mockApi.get.mockResolvedValueOnce({ data: messages });

    const { chatService } = await import('./chatService');
    const result = await chatService.getMessages(42);

    expect(mockApi.get).toHaveBeenCalledWith(API_CONFIG.ENDPOINTS.MESSAGES, {
      headers: { receiver: '42' },
    });
    expect(result).toEqual(messages);
  });

  it('sends message payload', async () => {
    const sent = { id: 2, content: 'sent' };
    mockApi.post.mockResolvedValueOnce({ data: sent });

    const { chatService } = await import('./chatService');
    const result = await chatService.sendMessage(8, 'hi there');

    expect(mockApi.post).toHaveBeenCalledWith(API_CONFIG.ENDPOINTS.MESSAGES, {
      receiver: 8,
      content: 'hi there',
    });
    expect(result).toEqual(sent);
  });

  it('gets all users', async () => {
    const users = [{ id: 7, email: 'u@x.com' }];
    mockApi.get.mockResolvedValueOnce({ data: users });

    const { chatService } = await import('./chatService');
    const result = await chatService.getAllUsers();

    expect(mockApi.get).toHaveBeenCalledWith(API_CONFIG.ENDPOINTS.ALL_USERS);
    expect(result).toEqual(users);
  });
});
