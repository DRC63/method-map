import { createContext, useCallback, useContext, useState } from 'react';
import { api, getAdminPassword, setAdminPassword } from '../api/client';

const AdminContext = createContext(null);

export function AdminProvider({ children }) {
  const [isAdmin, setIsAdmin] = useState(Boolean(getAdminPassword()));

  const unlock = useCallback(async (password) => {
    const { ok } = await api.verifyPassword(password);
    if (ok) {
      setAdminPassword(password);
      setIsAdmin(true);
    }
    return ok;
  }, []);

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

export function useAdmin() {
  const ctx = useContext(AdminContext);
  if (!ctx) throw new Error('useAdmin must be used within AdminProvider');
  return ctx;
}
