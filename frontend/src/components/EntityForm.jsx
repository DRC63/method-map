import { useState } from 'react';
import { api } from '../api/client';
import Modal from './Modal';

// NOTE: these Type and Product-group options are the PRINCE2 vocabulary. Unlike
// the rest of the app (which reads the framework's own config types), this admin
// form has not yet been generalised, so authoring an MSP/SAFe/PMBOK-specific type
// (event, knowledge-area, tool, …) isn't offered here — a known limitation.
const TYPES = ['process', 'activity', 'role', 'practice', 'approach', 'product'];
const SUBGROUPS = { '': '—', baseline: 'Baseline', log: 'Project Log', report: 'Report' };

// Create/edit form for a single entity, shown in a modal in authoring mode.
// `entity` is null in create mode and the existing entity in edit mode.
export default function EntityForm({ frameworkId, entity, processes, onClose, onSaved }) {
  const editing = Boolean(entity);
  const [form, setForm] = useState({
    type: entity?.type || 'role',
    name: entity?.name || '',
    code: entity?.code || '',
    subgroup: entity?.subgroup || '',
    parent_id: entity?.parent_id || '',
    confidence: entity?.confidence || 'confirmed',
    description: entity?.description || '',
  });
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    // Normalise before sending: trim text, send null (not "") for empty optional
    // fields, and only attach a parent process for activities — the parent_id has
    // no meaning for any other type.
    const payload = {
      type: form.type,
      name: form.name.trim(),
      code: form.code.trim() || null,
      subgroup: form.subgroup || null,
      parent_id: form.type === 'activity' && form.parent_id ? Number(form.parent_id) : null,
      confidence: form.confidence,
      description: form.description.trim() || null,
    };
    try {
      if (editing) await api.updateEntity(entity.id, payload);
      else await api.createEntity({ ...payload, framework_id: frameworkId });
      onSaved();
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  return (
    <Modal title={editing ? 'Edit entity' : 'Add entity'} onClose={onClose}>
      <form onSubmit={submit}>
        <div className="form-row">
          <div className="form-field">
            <label>Type</label>
            <select value={form.type} onChange={set('type')}>
              {TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div className="form-field">
            <label>Code (optional)</label>
            <input value={form.code} onChange={set('code')} placeholder="e.g. SU" />
          </div>
        </div>
        <div className="form-field">
          <label>Name</label>
          <input value={form.name} onChange={set('name')} required />
        </div>
        {form.type === 'activity' && (
          <div className="form-field">
            <label>Owning process</label>
            <select value={form.parent_id} onChange={set('parent_id')}>
              <option value="">— none —</option>
              {processes.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
        )}
        <div className="form-row">
          {form.type === 'product' && (
            <div className="form-field">
              <label>Product group</label>
              <select value={form.subgroup} onChange={set('subgroup')}>
                {Object.entries(SUBGROUPS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </div>
          )}
          <div className="form-field">
            <label>Confidence</label>
            <select value={form.confidence} onChange={set('confidence')}>
              <option value="confirmed">confirmed</option>
              <option value="indicative">indicative</option>
            </select>
          </div>
        </div>
        <div className="form-field">
          <label>Description (optional)</label>
          <textarea rows={2} value={form.description} onChange={set('description')} />
        </div>
        {error && <div className="banner" style={{ marginBottom: 12 }}>{error}</div>}
        <div className="form-actions">
          <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
