import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ChatAuthShell } from './ChatAuthShell';

vi.mock('./ChatWorkspace', () => ({
  ChatWorkspace: ({
    activeConversationId,
  }: {
    activeConversationId?: string;
  }) => <div>active conversation: {activeConversationId || '(none)'}</div>,
}));

describe('ChatAuthShell routing', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('passes the route conversation id to ChatWorkspace', async () => {
    render(
      <MemoryRouter initialEntries={['/chat/conv-123']}>
        <Routes>
          <Route path="/chat/:conversationId" element={<ChatAuthShell />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(
      await screen.findByText('active conversation: conv-123'),
    ).toBeInTheDocument();
  });
});
