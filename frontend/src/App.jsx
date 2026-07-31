import { BrowserRouter, Route, Routes } from 'react-router';
import AppLayout from './layout/AppLayout';
import { AdminProvider } from './context/AdminContext';
import Explorer from './pages/Explorer';
import Lifecycle from './pages/Lifecycle';
import Guide from './pages/Guide';
import Admin from './pages/Admin';

export default function App() {
  return (
    <AdminProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={
              <AppLayout title="Method Explorer" fluid>
                <Explorer />
              </AppLayout>
            }
          />
          <Route
            path="/lifecycle"
            element={
              <AppLayout title="Project Lifecycle" fluid>
                <Lifecycle />
              </AppLayout>
            }
          />
          <Route
            path="/guide"
            element={
              <AppLayout title="Guide">
                <Guide />
              </AppLayout>
            }
          />
          <Route
            path="/admin"
            element={
              <AppLayout title="Authoring &amp; Admin">
                <Admin />
              </AppLayout>
            }
          />
        </Routes>
      </BrowserRouter>
    </AdminProvider>
  );
}
