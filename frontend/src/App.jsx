import { BrowserRouter, Route, Routes } from 'react-router';
import AppLayout from './layout/AppLayout';
import { AdminProvider } from './context/AdminContext';
import Explorer from './pages/Explorer';
import Lifecycle from './pages/Lifecycle';
import Guide from './pages/Guide';
import Admin from './pages/Admin';
import { useDeploymentFramework } from './lib/useDeploymentFramework';
import { lifecycleLabel } from './theme/labels';

// Serve under the Vite base path (e.g. '/prince2') when deployed behind the
// shared apps.p3mai.com front door; '/' (default) locally and at the root.
const basename = import.meta.env.BASE_URL.replace(/\/$/, '') || undefined;

// The lifecycle page's header follows the framework: "Project Lifecycle" for
// PRINCE2, "Programme Lifecycle" for MSP.
function LifecycleLayout({ children }) {
  const fw = useDeploymentFramework();
  return (
    <AppLayout title={lifecycleLabel(fw)} fluid>
      {children}
    </AppLayout>
  );
}

export default function App() {
  return (
    <AdminProvider>
      <BrowserRouter basename={basename}>
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
              <LifecycleLayout>
                <Lifecycle />
              </LifecycleLayout>
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
