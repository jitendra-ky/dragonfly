import * as typesModule from './index';

describe('types module', () => {
  it('loads without runtime exports', () => {
    expect(typeof typesModule).toBe('object');
    expect(typesModule.default).toBeUndefined();
  });
});
