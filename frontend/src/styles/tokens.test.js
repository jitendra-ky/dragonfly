
import { colors, spacing, typography, borderRadius, shadows, breakpoints } from './tokens';

describe('style tokens', () => {
  it('exports color and spacing scales', () => {
    expect(colors.primary[600]).toBe('#2563eb');
    expect(spacing.lg).toBe('1.5rem');
  });

  it('exports typography, radius, shadows and breakpoints', () => {
    expect(typography.fontFamily.sans[0]).toBe('Inter');
    expect(borderRadius.full).toBe('9999px');
    expect(shadows.md).toContain('rgb');
    expect(breakpoints.lg).toBe('1024px');
  });
});
/* eslint-env jest */
