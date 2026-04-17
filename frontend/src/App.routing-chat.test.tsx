import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import App from './App';

vi.mock('@/features/chat/ChatWorkspace', () => ({
  ChatWorkspace: ({
    activeConversationId,
  }: {
    activeConversationId?: string;
  }) => <div>app route active conversation: {activeConversationId || '(none)'}</div>,
}));

describe('App chat routing integration', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('passes /chat/:conversationId through the full app route tree', async () => {
    window.history.pushState({}, '', '/chat/conv-xyz');

    render(<App />);

    expect(
      await screen.findByText('app route active conversation: conv-xyz'),
    ).toBeInTheDocument();
  });
});
