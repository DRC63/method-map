import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useAdmin } from '../context/AdminContext';

// Right-hand panel shown when an entity is selected in the graph. It fetches the
// entity's full detail (name, description, confidence, and every relationship it
// takes part in) and lists those relationships, grouped and worded to match the
// entity's role in the model. Export buttons (PDF/CSV for this one entity) are
// always available; edit/delete/add-relationship appear only in authoring mode.

// One relationship line in the list: a coded pill, the related entity's name and
// the code's meaning, and a colour dot for its type. Clicking it selects that
// entity, so the panel doubles as a way to walk the graph.
function RelatedRow({ rel, onSelect, colorOf, codeColors }) {
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

  // Reload the detail whenever the selected entity changes, or when reloadToken
  // is bumped after an edit. The `alive` flag guards against a slow response
  // arriving after the user has already moved on — without it, a stale fetch
  // could overwrite the newer selection.
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

  // Relationships are stored as hub → target, so "outgoing" are the links this
  // entity is the source of and "incoming" are the ones pointing at it. Which set
  // is meaningful depends on the entity's role (see the sections below).
  const outgoing = detail.related.filter((r) => r.direction === 'out');
  const incoming = detail.related.filter((r) => r.direction === 'in');

  // A bundled worked-example PDF for this entity, if the framework config lists one
  // (currently the PRINCE2 products → Helios sample documents). Undefined otherwise.
  const examplePath = theme.examples?.[detail.name];

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
        {/* Worked-example document, when this entity has one in the framework
            config's `examples` map. The value is a bundled PDF path relative to the
            SPA base, so it resolves correctly both locally ("/…") and behind the
            front door ("/prince2/…"). Opens in a new tab; distinct from the
            "PDF summary" below, which is the generated per-entity relationship report. */}
        {examplePath && (
          <div style={{ marginTop: 12 }}>
            <a
              className="btn btn-accent btn-sm"
              href={`${import.meta.env.BASE_URL}${examplePath}`}
              target="_blank"
              rel="noreferrer"
              style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%' }}
            >
              <span style={{ flex: 1, textAlign: 'left' }}>View worked example</span>
              <span aria-hidden="true">↗</span>
            </a>
            <div className="muted" style={{ fontSize: '0.72rem', marginTop: 4 }}>
              Helios worked example · PDF, opens in a new tab
            </div>
          </div>
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

      {/* The relationship list is worded to match the entity's role: a container
          (process/event) lists its child activities in sequence; a hub (activity)
          lists what it uses and produces; a node (role/product/tool…) lists the
          activities that reference it, plus any co-occurring links. */}
      <div className="detail-body">
        {detail.type === theme.container ? (
          <>
            <div className="detail-section-title">
              Activities in sequence ({outgoing.length})
            </div>
            {outgoing.length === 0 && <p className="muted">No activities recorded.</p>}
            {outgoing.map((r) => (
              <RelatedRow key={r.relationship_id} rel={r} onSelect={onSelect} colorOf={theme.colorOf} codeColors={theme.codeColors} />
            ))}
          </>
        ) : detail.type === theme.hub ? (
          <>
            <div className="detail-section-title">Uses / produces ({outgoing.length})</div>
            {outgoing.length === 0 && <p className="muted">No links recorded.</p>}
            {outgoing.map((r) => (
              <RelatedRow key={r.relationship_id} rel={r} onSelect={onSelect} colorOf={theme.colorOf} codeColors={theme.codeColors} />
            ))}
          </>
        ) : (
          <>
            <div className="detail-section-title">
              Referenced by activities ({incoming.length})
            </div>
            {incoming.length === 0 && <p className="muted">No links recorded.</p>}
            {incoming.map((r) => (
              <RelatedRow key={r.relationship_id} rel={r} onSelect={onSelect} colorOf={theme.colorOf} codeColors={theme.codeColors} />
            ))}
          </>
        )}
        {detail.type !== theme.hub && detail.type !== theme.container && outgoing.length > 0 && (
          <>
            <div className="detail-section-title">Also links to ({outgoing.length})</div>
            {outgoing.map((r) => (
              <RelatedRow key={r.relationship_id} rel={r} onSelect={onSelect} colorOf={theme.colorOf} codeColors={theme.codeColors} />
            ))}
          </>
        )}
      </div>
    </aside>
  );
}
