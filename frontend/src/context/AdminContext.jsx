// Authoring-mode authentication state, shared across the app through React context.
//
// Editing (create/update/delete) is gated by a single shared admin password rather
// than per-user accounts — a deliberate, lightweight choice for an open reference
// tool with no personal data. The password is held in the browser's localStorage
// (see api/client.js); this context only tracks whether the current browser is
// unlocked and exposes the unlock/lock actions.
import { createContext, useCallback, useContext, useState } from 'react';
import { api, getAdminPassword, setAdminPassword } from '../api/client';

const AdminContext = createContext(null);

export function AdminProvider({ children }) {
  // Treat the browser as already unlocked if a password is present from a prior
  // session, so an editor isn't asked to re-enter it on every reload.
  const [isAdmin, setIsAdmin] = useState(Boolean(getAdminPassword()));

  // Verify the password against the server BEFORE storing it, so a wrong entry
  // never gets saved and every later write is guaranteed to be accepted.
  const unlock = useCallback(async (password) => {
    const { ok } = await api.verifyPassword(password);
    if (ok) {
      setAdminPassword(password);
      setIsAdmin(true);
    }
    return ok;
  }, []);

  // Clear the stored password and drop back to read-only mode.
  const lock = useCallback(() => {
    setAdminPassword('');
    setIsAdmin(false);
  }, []);

  return (
    <AdminContext.Provider value={{ isAdmin, unlock, lock }}>
      {children}
    </AdminContext.Provider>
  );
}

// Convenience hook for consumers; throws if used outside the provider so the
// mistake surfaces immediately rather than as a confusing null-context error.
export function useAdmin() {
  const ctx = useContext(AdminContext);
  if (!ctx) throw new Error('useAdmin must be used within AdminProvider');
  return ctx;
}
