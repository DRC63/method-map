import { useEffect, useState } from 'react';
import { NavLink } from 'react-router';
import logo from '../assets/logo-triangle-white.svg';
import { api } from '../api/client';
import { useAdmin } from '../context/AdminContext';
import { lifecycleLabel } from '../theme/labels';

const LINKS = [
  { to: '/', label: 'Method Explorer', end: true },
  { to: '/lifecycle', label: 'Project Lifecycle' },
  { to: '/guide', label: 'Guide' },
  { to: '/admin', label: 'Authoring & Admin' },
];

// Points at the local static-site server while on localhost; swaps to the real
// domain automatically once served from its own subdomain, so there's nothing
// to change at deploy time.
const isLocal = /^(localhost|127\.0\.0\.1)$/.test(window.location.hostname);
const WEBSITE_URL = isLocal
  ? 'http://localhost:4173/services.html'
  : 'https://p3mai.com/services.html';

export default function Sidebar() {
  const { isAdmin } = useAdmin();
  // Each deployment is a single framework; label the app with it so PRINCE2 vs
  // MSP is clear in the title (and the browser tab), not just the graph content.
  const [title, setTitle] = useState('Method Map');
  const [lifecycleLbl, setLifecycleLbl] = useState('Project Lifecycle');
  useEffect(() => {
    api
      .listFrameworks()
      .then((list) => {
        const fw = list?.[0];
        setLifecycleLbl(lifecycleLabel(fw));
        const name = fw?.name;
        if (name) {
          const t = `${name} Method Map`;
          setTitle(t);
          document.title = `${t} | P3MAI`;
        }
      })
      .catch(() => {});
  }, []);

  const links = LINKS.map((l) =>
    l.to === '/lifecycle' ? { ...l, label: lifecycleLbl } : l,
  );

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img src={logo} alt="P3MAI" />
        <span>{title}</span>
      </div>
      <nav className="sidebar-nav">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => (isActive ? 'active' : undefined)}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
      {isAdmin && (
        <div className="sidebar-admin-status">
          Authoring mode <strong>unlocked</strong>
        </div>
      )}
      <a className="sidebar-back" href={WEBSITE_URL}>
        <span aria-hidden="true">&larr;</span> Back to Website
      </a>
    </aside>
  );
}
