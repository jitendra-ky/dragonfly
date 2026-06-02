import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import Button from './Button'

describe('Button', () => {
  it('renders label', () => {
    render(<Button>Send</Button>)
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('calls onClick when pressed', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()

    render(<Button onClick={onClick}>Send</Button>)
    await user.click(screen.getByRole('button', { name: /send/i }))

    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Send</Button>)
    expect(screen.getByRole('button', { name: /send/i })).toBeDisabled()
  })
})
