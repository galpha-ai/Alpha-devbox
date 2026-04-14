import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  clearAuthSession,
  createAuthClient,
  ensureMockAuthSession,
  resolveLocalDevUserId,
  resolveApiBaseUrl,
} from './auth';
import { createChatTransportClient } from './transport';
import { ChatWorkspace } from './ChatWorkspace';

export function ChatAuthShell() {
  const [localUserId] = useState(() =>
    resolveLocalDevUserId(
      window.localStorage,
      import.meta.env.VITE_THESIS_LOCAL_USER_ID,
    ),
  );

  return (
    <ChatSeededSessionRuntime localUserId={localUserId} />
  );
}

function ChatSeededSessionRuntime({
  localUserId,
}: {
  localUserId: string;
}) {
  const { transportClient } = useChatClients();
  const [, setSession] = useState(() =>
    ensureMockAuthSession(window.localStorage, localUserId),
  );

  useEffect(() => {
    setSession(ensureMockAuthSession(window.localStorage, localUserId));
  }, [localUserId]);

  const handleResetSession = useCallback(() => {
    setSession(ensureMockAuthSession(window.localStorage, localUserId));
  }, [localUserId]);

  const handleSessionExpired = useCallback(() => {
    clearAuthSession(window.localStorage);
    setSession(ensureMockAuthSession(window.localStorage, localUserId));
  }, [localUserId]);

  return (
    <ChatWorkspace
      transportClient={transportClient}
      sessionActionLabel={null}
      onLogout={handleResetSession}
      onSessionExpired={handleSessionExpired}
    />
  );
}

function useChatClients() {
  const baseUrl = useMemo(
    () =>
      resolveApiBaseUrl(
        import.meta.env.DEV,
        import.meta.env.VITE_API_URL,
        typeof window !== 'undefined' ? window.location.origin : '',
      ),
    [],
  );

  const authClient = useMemo(() => createAuthClient({ baseUrl }), [baseUrl]);
  const transportClient = useMemo(
    () => createChatTransportClient({ authFetch: authClient.authFetch }),
    [authClient],
  );

  return {
    transportClient,
  };
}
