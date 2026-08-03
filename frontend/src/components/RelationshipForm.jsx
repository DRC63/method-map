import { useMemo, useState } from 'react';
import { api } from '../api/client';
import Modal from './Modal';

// PRINCE2 code sets (same known limitation as EntityForm — not yet read from the
// framework config, so the SAFe/MSP/PMBOK code vocabularies aren't offered here).
const ROLE_CODES = ['C', 'P', 'N'];
const PRODUCT_CODES = ['I', 'O', 'U', 'A'];

// Add-relationship form (activity → role/practice/approach/product, with a code),
// shown in a modal in authoring mode. `presetFrom`/`presetTo` pre-fill one endpoint
// from the entity the editor started from. New relationships are saved as
// 'indicative' because anything entered by hand is, by definition, unverified until
// an SME confirms it against the licensed source.
export default function RelationshipForm({ frameworkId, entities, presetFrom, presetTo, onClose, onSaved }) {
  const activities = useMemo(
    () => entities.filter((e) => e.type === 'activity'),
    [entities],
  );
  const targets = useMemo(
    () => entities.filter((e) => e.type !== 'activity' && e.type !== 'process'),
    [entities],
  );

  const [fromId, setFromId] = useState(presetFrom || activities[0]?.id || '');
  const [toId, setToId] = useState(presetTo || targets[0]?.id || '');
  const [code, setCode] = useState('C');
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const toEntity = entities.find((e) => e.id === Number(toId));
  const codeOptions = toEntity?.type === 'product' ? PRODUCT_CODES : ROLE_CODES;

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await api.createRelationship({
        framework_id: frameworkId,
        from_entity_id: Number(fromId),
        to_entity_id: Number(toId),
        code,
        confidence: 'indicative',
      });
      onSaved();
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  return (
    <Modal title="Add relationship" onClose={onClose}>
      <form onSubmit={submit}>
        <div className="form-field">
          <label>Activity</label>
          <select value={fromId} onChange={(e) => setFromId(e.target.value)}>
            {activities.map((a) => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>
        </div>
        <div className="form-field">
          <label>Target (role / practice / approach / product)</label>
          <select value={toId} onChange={(e) => setToId(e.target.value)}>
            {targets.map((t) => (
              <option key={t.id} value={t.id}>{t.type} · {t.name}</option>
            ))}
          </select>
        </div>
        <div className="form-field">
          <label>Code</label>
          <select value={code} onChange={(e) => setCode(e.target.value)}>
            {codeOptions.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
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
