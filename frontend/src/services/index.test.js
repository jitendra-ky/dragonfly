
/* eslint-env jest */
import * as services from './index';

describe('services index', () => {
  it('re-exports service modules', () => {
    expect(services.authService).toBeDefined();
    expect(services.chatService).toBeDefined();
    expect(services.api).toBeDefined();
  });
});
