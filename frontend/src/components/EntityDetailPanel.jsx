import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { codeColors } from '../theme/theme';
import { useAdmin } from '../context/AdminContext';

function RelatedRow({ rel, onSelect, colorOf }) {
  // Known relationship codes get their code colour; numeric "step N" pills
  // (a container's child hubs) get the related node's own type colour.
  const pillColor = codeColors[rel.code] || colorOf(rel.type);
  return (
    <div className="related-row" onClick={() => onSelect(rel.entity_id)}>
      <span className="code-pill" style={{ background: pillColor }}>
        {rel.code}
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="related-name">{rel.name}</div>
        <div className="related-sub">
          {rel.code_label}
          {rel.via_process ? ` · ${rel.via_process}` : ''}
        </div>
      </div>
      <span
        className="layer-swatch"
        style={{ background: colorOf(rel.type), borderRadius: '50%' }}
        title={rel.type}
      />
    </div>
  );
}

export default function EntityDetailPanel({
  frameworkKey,
  theme,
  entityId,
  onSelect,
  onClose,
  onEdit,
  onAddRelationship,
  onChanged,
  reloadToken,
}) {
  const { isAdmin } = useAdmin();
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    api.getEntity(entityId).then((d) => {
      if (alive) {
        setDetail(d);
        setLoading(false);
      }
    });
    return () => {
      alive = false;
    };
  }, [entityId, reloadToken]);

  if (loading || !detail) {
    return (
      <aside className="detail-panel">
        <div className="detail-body muted">Loading…</div>
      </aside>
    );
  }

  const outgoing = detail.related.filter((r) => r.direction === 'out');
  const incoming = detail.related.filter((r) => r.direction === 'in');

  const remove = async () => {
    if (!window.confirm(`Delete "${detail.name}" and all its relationships?`)) return;
    await api.deleteEntity(detail.id);
    onClose();
    onChanged();
  };

  return (
    <aside className="detail-panel">
      <div className="detail-header">
        <button className="detail-close" onClick={onClose} aria-label="Close">×</button>
        <span className="detail-type-chip" style={{ background: theme.colorOf(detail.type) }}>
          {detail.type}
        </span>
        <h2>{detail.name}</h2>
        <div className="detail-meta">
          {detail.code ? `${detail.code} · ` : ''}
          {theme.labelOf(detail.type)}
          {detail.parent_name ? ` · ${detail.parent_name}` : ''}
        </div>
        <div style={{ marginTop: 8 }}>
          <span className={`confidence-flag confidence-${detail.confidence}`}>
            {detail.confidence === 'indicative' ? '◌ indicative' : '✓ confirmed'}
          </span>
        </div>
        {detail.description && (
          <p style={{ marginTop: 10, fontSize: '0.85rem' }}>{detail.description}</p>
        )}
        <div className="admin-actions">
          <a className="btn btn-outline btn-sm" href={api.pdfUrl(frameworkKey, detail.id)} target="_blank" rel="noreferrer">
            PDF summary
          </a>
          <a className="btn btn-outline btn-sm" href={api.csvUrl(frameworkKey, detail.id)}>
            CSV (this entity)
          </a>
        </div>
        {isAdmin && (
          <div className="admin-actions">
            <button className="btn btn-accent btn-sm" onClick={() => onEdit(detail)}>Edit</button>
            <button className="btn btn-outline btn-sm" onClick={() => onAddRelationship(detail)}>
              + Relationship
            </button>
            <button className="btn btn-danger btn-sm" onClick={remove}>Delete</button>
          </div>
        )}
      </div>

      <div className="detail-body">
        {detail.type === theme.container ? (
          <>
            <div className="detail-section-title">
              Activities in sequence ({outgoing.length})
            </div>
            {outgoing.length === 0 && <p className="muted">No activities recorded.</p>}
            {outgoing.map((r) => (
              <RelatedRow key={r.relationship_id} rel={r} onSelect={onSelect} colorOf={theme.colorOf} />
            ))}
          </>
        ) : detail.type === theme.hub ? (
          <>
            <div className="detail-section-title">Uses / produces ({outgoing.length})</div>
            {outgoing.length === 0 && <p className="muted">No links recorded.</p>}
            {outgoing.map((r) => (
              <RelatedRow key={r.relationship_id} rel={r} onSelect={onSelect} colorOf={theme.colorOf} />
            ))}
          </>
        ) : (
          <>
            <div className="detail-section-title">
              Referenced by activities ({incoming.length})
            </div>
            {incoming.length === 0 && <p className="muted">No links recorded.</p>}
            {incoming.map((r) => (
              <RelatedRow key={r.relationship_id} rel={r} onSelect={onSelect} colorOf={theme.colorOf} />
            ))}
          </>
        )}
        {detail.type !== theme.hub && detail.type !== theme.container && outgoing.length > 0 && (
          <>
            <div className="detail-section-title">Also links to ({outgoing.length})</div>
            {outgoing.map((r) => (
              <RelatedRow key={r.relationship_id} rel={r} onSelect={onSelect} colorOf={theme.colorOf} />
            ))}
          </>
        )}
      </div>
    </aside>
  );
}
