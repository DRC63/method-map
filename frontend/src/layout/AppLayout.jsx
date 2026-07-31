import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function AppLayout({ title, children, fluid = false }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="content-area">
        <Topbar title={title} />
        <main className={fluid ? 'page-content' : 'page-content padded'}>
          {children}
        </main>
      </div>
    </div>
  );
}
