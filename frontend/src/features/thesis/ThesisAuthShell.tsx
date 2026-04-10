import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  clearAuthSession,
  createThesisAuthClient,
  ensureMockAuthSession,
  resolveThesisApiBaseUrl,
} from './auth';
import { createThesisTransportClient } from './transport';
import { ThesisWorkspace } from './ThesisWorkspace';

const DEFAULT_THESIS_MOCK_USER_ID = 'thesis-demo-user';

export function ThesisAuthShell() {
  return (
    <ThesisSeededSessionRuntime
      localUserId={
        import.meta.env.VITE_THESIS_LOCAL_USER_ID?.trim() ||
        DEFAULT_THESIS_MOCK_USER_ID
      }
    />
  );
}

function ThesisSeededSessionRuntime({
  localUserId,
}: {
  localUserId: string;
}) {
  const { transportClient } = useThesisClients();
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
    <ThesisWorkspace
      transportClient={transportClient}
      sessionActionLabel={null}
      onLogout={handleResetSession}
      onSessionExpired={handleSessionExpired}
    />
  );
}

function useThesisClients() {
  const baseUrl = useMemo(
    () =>
      resolveThesisApiBaseUrl(
        import.meta.env.DEV,
        import.meta.env.VITE_API_URL,
        typeof window !== 'undefined' ? window.location.origin : '',
      ),
    [],
  );

  const authClient = useMemo(() => createThesisAuthClient({ baseUrl }), [baseUrl]);
  const transportClient = useMemo(
    () => createThesisTransportClient({ authFetch: authClient.authFetch }),
    [authClient],
  );

  return {
    authClient,
    transportClient,
  };
}
