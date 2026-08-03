import { api } from '../api/client';

// The left-hand control panel for the Method Explorer, with five sections: Search,
// Layout (Matrix/Timeline plus a one-line description), Layers (toggle each entity
// type on/off and the indirect-links switch), Edge codes (the legend), and Export.
//
// It is presentational: all state lives in Explorer and is passed in as props, and
// user actions are reported back up through the callbacks (onSearch, onSetLayout,
// onToggleType, …). Every label, colour, lane name and edge code is read from the
// framework `theme`, so the panel names the right things for any framework without
// hardcoding one method's terminology.
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
  // Swimlane names come from the framework config (Directing/Managing/Delivering
  // for PRINCE2, Sponsoring/Managing/Delivering for MSP), stripped of their
  // parenthetical role gloss.
  const laneNames = (theme?.lanes || [])
    .map((l) => l.label.replace(/\s*\(.*$/, ''))
    .join(' / ');

  // Matrix blurb describes each layer's fixed zone, pulled from the framework
  // config so it names the right layers (PRINCE2: roles/practices/approaches;
  // MSP: roles/themes/principles) instead of hardcoding PRINCE2's.
  const zoneLabel = (z) => (theme?.types || []).find((t) => t.zone === z)?.label || '';
  const matrixBlurb = theme
    ? `Fixed hierarchy: ${theme.labelOf(theme.container)} top, ${theme.labelOf(theme.hub)} below, ${zoneLabel('below')} under; ${zoneLabel('left')} left, ${zoneLabel('right')} right, ${zoneLabel('bottom')} bottom.`
    : '';
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
            ? `Lifecycle swimlanes (${laneNames}) left→right in sequence, with resource bands below. Scrub the timeline to light up each stage.`
            : matrixBlurb}
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
        {(theme?.codeGroups || []).flatMap((g) => g.codes).map(({ code, label, color }) => (
          <div key={code} className="legend-item">
            <span className="legend-line" style={{ borderTopColor: color }} />
            <strong style={{ color }}>{code}</strong>&nbsp;{label}
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
