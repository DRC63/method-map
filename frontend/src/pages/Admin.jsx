import { useState } from 'react';
import { useAdmin } from '../context/AdminContext';

export default function Admin() {
  const { isAdmin, unlock, lock } = useAdmin();
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const ok = await unlock(password);
      if (!ok) setError('Incorrect password.');
      setPassword('');
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (isAdmin) {
    return (
      <div className="prose">
        <div className="card section-gap">
          <h2 style={{ marginTop: 0 }}>Authoring mode is unlocked</h2>
          <p>
            You can now edit the map. In the <strong>Method Explorer</strong>:
          </p>
          <ul className="bullets">
            <li><strong>+ Add entity</strong> (top-right of the graph) creates a process, activity, role, practice, approach or product.</li>
            <li>Click any node, then use <strong>Edit</strong>, <strong>+ Relationship</strong> or <strong>Delete</strong> in its detail panel.</li>
            <li>Set an item's confidence to <em>confirmed</em> once you've verified it against the licensed manual — the dashed “indicative” ring disappears.</li>
          </ul>
          <p className="muted">
            This is a lightweight single-password gate — enough to stop casual edits on
            an open deployment, not full user accounts.
          </p>
          <button className="btn btn-outline" onClick={lock}>Lock authoring mode</button>
        </div>
      </div>
    );
  }

  return (
    <div className="prose">
      <div className="card" style={{ maxWidth: 420 }}>
        <h2 style={{ marginTop: 0 }}>Authoring &amp; Admin</h2>
        <p>Enter the admin password to unlock editing.</p>
        <form onSubmit={submit}>
          <div className="form-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoFocus
            />
          </div>
          {error && <div className="banner" style={{ marginBottom: 12 }}>{error}</div>}
          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={busy || !password}>
              {busy ? 'Checking…' : 'Unlock'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
