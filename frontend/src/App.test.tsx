import { useEffect, useState } from 'react';
import { act, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import App from './App';

let webChatMountCount = 0;

function WebChatPageMock() {
  const [mountId, setMountId] = useState(0);

  useEffect(() => {
    webChatMountCount += 1;
    setMountId(webChatMountCount);
  }, []);

  return <div>Web chat page mounts: {mountId}</div>;
}

vi.mock('./pages/WebChatPage.tsx', () => ({
  default: WebChatPageMock,
}));

vi.mock('./pages/ReplayPage.tsx', () => ({
  default: () => <div>Replay page</div>,
}));

describe('App routes', () => {
  beforeEach(() => {
    webChatMountCount = 0;
    window.history.pushState({}, '', '/');
  });

  it('renders the web chat page for direct conversation routes', async () => {
    window.history.pushState({}, '', '/chat/conv-123');

    render(
      <App />,
    );

    expect(await screen.findByText('Web chat page mounts: 1')).toBeInTheDocument();
  });

  it('keeps the web chat page mounted when moving from root to /chat/:conversationId', async () => {
    render(<App />);

    expect(await screen.findByText('Web chat page mounts: 1')).toBeInTheDocument();

    await act(async () => {
      window.history.pushState({}, '', '/chat/conv-123');
      window.dispatchEvent(new PopStateEvent('popstate'));
    });

    expect(await screen.findByText('Web chat page mounts: 1')).toBeInTheDocument();
  });
});
