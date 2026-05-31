import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Modal from './Modal';

describe('Modal', () => {
  it('does not render when closed', () => {
    render(
      <Modal isOpen={false} onClose={() => {}} title="Dialog">
        Body
      </Modal>
    );
    expect(screen.queryByText('Dialog')).not.toBeInTheDocument();
  });

  it('renders when open and triggers close actions', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <Modal isOpen onClose={onClose} title="Dialog">
        Body
      </Modal>
    );

    expect(screen.getByText('Dialog')).toBeInTheDocument();
    expect(screen.getByText('Body')).toBeInTheDocument();

    const closeButton = screen.getAllByRole('button')[0];
    await user.click(closeButton);
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
