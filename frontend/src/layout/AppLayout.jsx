import Sidebar from './Sidebar';
import Topbar from './Topbar';

// Standard page frame used by every route: left sidebar navigation, a top bar
// (page title + brand), and the routed page content.
//
// `fluid` controls the content padding. Graph and timeline pages pass fluid=true
// so the visualisation can use the full area; text pages (Guide, Admin) leave it
// false to keep a comfortable padded reading width.
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
