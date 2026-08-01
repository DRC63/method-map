import { api } from '../api/client';
import { codeColors } from '../theme/theme';

export default function ControlPanel({
  frameworkKey,
  theme,
  counts,
  visibleTypes,
  onToggleType,
  derived,
  onToggleDerived,
  layout,
  onSetLayout,
  search,
  onSearch,
  onExportPng,
}) {
  return (
    <div className="control-panel">
      <div className="control-group">
        <h3>Search</h3>
        <input
          className="search-input"
          placeholder="Find a role, product, activity…"
          value={search}
          onChange={(e) => onSearch(e.target.value)}
        />
      </div>

      <div className="control-group">
        <h3>Layout</h3>
        <div className="layout-switch">
          <button
            className={`layout-opt ${layout === 'structured' ? 'active' : ''}`}
            onClick={() => onSetLayout('structured')}
          >
            Matrix
          </button>
          <button
            className={`layout-opt ${layout === 'timeline' ? 'active' : ''}`}
            onClick={() => onSetLayout('timeline')}
          >
            Timeline
          </button>
        </div>
        <p className="muted" style={{ marginTop: 8, fontSize: '0.76rem' }}>
          {layout === 'timeline'
            ? 'Lifecycle swimlanes (Directing / Managing / Delivering) left→right in sequence, with resource bands below. Scrub the timeline to light up each stage.'
            : 'Fixed hierarchy: processes top, activities below, products under; roles left, practices right, approaches bottom.'}
        </p>
      </div>

      <div className="control-group">
        <h3>Layers</h3>
        {(theme?.types || []).map((t) => {
          const on = visibleTypes.has(t.key);
          return (
            <label key={t.key} className={`layer-toggle ${on ? '' : 'off'}`}>
              <input type="checkbox" checked={on} onChange={() => onToggleType(t.key)} />
              <span className="layer-swatch" style={{ background: t.color }} />
              <span className="layer-name">{t.label}</span>
              <span className="layer-count">{counts[t.key] ?? 0}</span>
            </label>
          );
        })}
        <label className="toggle-switch" style={{ marginTop: 10 }}>
          <input type="checkbox" checked={derived} onChange={onToggleDerived} />
          Show indirect (co-occurrence) links
        </label>
      </div>

      <div className="control-group">
        <h3>Edge codes</h3>
        {[
          ['C', 'Responsible'], ['P', 'Participates'], ['N', 'Assists'],
          ['I', 'Input'], ['O', 'Output'], ['U', 'Update'], ['A', 'Authorise'],
        ].map(([c, label]) => (
          <div key={c} className="legend-item">
            <span className="legend-line" style={{ borderTopColor: codeColors[c] }} />
            <strong style={{ color: codeColors[c] }}>{c}</strong>&nbsp;{label}
          </div>
        ))}
        <div className="legend-item">
          <span className="legend-line" style={{ borderTopColor: 'rgba(120,130,145,0.5)' }} />
          Structure / indirect link
        </div>
        <div className="legend-item">
          <span className="layer-swatch" style={{ border: '1.4px dashed #A8841C', background: 'transparent', borderRadius: '50%' }} />
          Dashed ring = indicative data
        </div>
      </div>

      <div className="control-group">
        <h3>Export</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <button className="btn btn-outline btn-sm" onClick={onExportPng}>Graph as PNG</button>
          <a className="btn btn-outline btn-sm" href={api.csvUrl(frameworkKey)}>Full data (CSV)</a>
          <a className="btn btn-outline btn-sm" href={api.xlsxUrl(frameworkKey)}>Full data (Excel)</a>
        </div>
      </div>
    </div>
  );
}
