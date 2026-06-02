import { render, screen } from '@testing-library/react'
import Avatar from './Avatar'

describe('Avatar', () => {
  it('renders initials and custom size', () => {
    render(<Avatar name="Jane Doe" size="lg" />)
    expect(screen.getByText('JD')).toBeInTheDocument()
  })

  it('renders initials from name', () => {
    const { getByText } = render(<Avatar name="John Doe" />)
    expect(getByText('JD')).toBeTruthy()
  })
})
