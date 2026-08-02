import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router';
import { api } from '../api/client';
import { lifecycleNoun } from '../theme/labels';

// Timeline columns come from the framework config: the phases flagged
// `column: true`, in order. "throughout" is drawn as a spanning bar; any other
// non-column phase folds into the repeating/delivery column.
const LANE_CLASSES = ['lane-directing', 'lane-managing', 'lane-delivering'];

// Frameworks with up to 3 lanes use the branded lane classes; a framework with
// more lanes (e.g. PMBOK's 10 Knowledge Areas) gets an evenly-spread generated
// palette so every swimlane row is visually distinct.
function laneVisual(index, total) {
  if (total <= LANE_CLASSES.length) {
    return { className: LANE_CLASSES[index % LANE_CLASSES.length] };
  }
  const hue = Math.round((index / total) * 360);
  return { style: { background: `hsl(${hue}deg 40% 30%)` } };
}

function ProcessCard({ p, active, onClick }) {
  const hasMeta = p.activities.length > 0 || p.repeats;
  return (
    <button
      className={`process-card ${p.lifecycle_phase === 'throughout' ? 'dp-bar' : ''} ${active ? 'active' : ''}`}
      onClick={() => onClick(p)}
    >
      <span className="pc-code">{p.code}</span>
      <span className="pc-name">{p.name}</span>
      {hasMeta && (
        <span className="pc-meta">
          {p.activities.length > 0 && <span>{p.activities.length} activities</span>}
          {p.repeats && <span className="pc-repeat">⟳ repeats each stage</span>}
        </span>
      )}
    </button>
  );
}

export default function Lifecycle() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    api.listFrameworks().then((list) => {
      const fw = list[0];
      if (!fw) return;
      api.getLifecycle(fw.key).then((lc) => {
        setData(lc);
        setSelected(lc.processes[0] || null);
      });
    });
  }, []);

  // Ordered column-phases (key/label/header) from the framework config.
  const phaseCols = useMemo(
    () => (data?.framework?.config?.phases || []).filter((p) => p.column),
    [data],
  );
  const deliveryKey = useMemo(
    () => phaseCols.find((c) => c.key === 'delivery')?.key || phaseCols[phaseCols.length - 1]?.key,
    [phaseCols],
  );
  const columnOf = useMemo(() => {
    const colKeys = new Set(phaseCols.map((c) => c.key));
    return (phase) => {
      if (phase === 'throughout') return null;
      if (colKeys.has(phase)) return phase;
      return deliveryKey; // fold any other non-column phase into the delivery column
    };
  }, [phaseCols, deliveryKey]);

  const byLevel = useMemo(() => {
    if (!data) return {};
    const out = {};
    data.level_order.forEach((lv) => {
      const procs = data.processes.filter((p) => p.lifecycle_level === lv);
      out[lv] = {
        throughout: procs.filter((p) => p.lifecycle_phase === 'throughout'),
        cols: phaseCols.map((col) =>
          procs.filter((p) => columnOf(p.lifecycle_phase) === col.key),
        ),
      };
    });
    return out;
  }, [data, phaseCols, columnOf]);

  if (!data) return <div className="graph-empty">Loading lifecycle…</div>;

  const spanCols = Math.max(1, phaseCols.length - 1);
  const noun = lifecycleNoun(data.framework);

  // The Lifecycle page assumes a linear project (Start → Close). A cyclic
  // framework (e.g. SAFe's repeating PI cadence) can override the framing via
  // config.timeline; otherwise fall back to the PRINCE2/MSP wording.
  const tl = data.framework?.config?.timeline || {};
  const introText =
    tl.intro ||
    `Time flows left to right across the ${noun}. Each swimlane is a level of ` +
      `responsibility; a process sits where it runs on the timeline. Delivery ` +
      `stages repeat until the ${noun} is done. Click any process to see its ` +
      `activities in sequence.`;
  const startLabel = tl.start_label || 'Start';
  const endLabel = tl.end_label || 'Close';
  const heading = tl.heading || `${data.framework.name} — the ${noun} lifecycle`;

  return (
    <div className="lifecycle-wrap">
      <div className="lifecycle-intro">
        <h2>{heading}</h2>
        <p>{introText}</p>
      </div>

      <div className="time-arrow">
        <span>{startLabel}</span>
        <span className="line" />
        <span>Time →</span>
        <span className="line" />
        <span>{endLabel}</span>
      </div>

      <div className="swimlane-grid" style={{ gridTemplateColumns: `auto repeat(${phaseCols.length}, 1fr)` }}>
        {/* header row */}
        <div className="grid-corner" />
        {phaseCols.map((col) => (
          <div key={col.key} className={`phase-header ${col.key === 'delivery' ? 'repeats' : ''}`}>
            {col.header || col.label || col.key}
            {col.key === 'delivery' && <span className="phase-note">⟳ one or more, repeating</span>}
          </div>
        ))}

        {/* swimlane rows */}
        {data.level_order.map((lv, li) => {
          const lane = byLevel[lv];
          const hasSpan = lane.throughout.length > 0;
          const vis = laneVisual(li, data.level_order.length);
          return (
            <div key={lv} style={{ display: 'contents' }}>
              <div className={`lane-label ${vis.className || ''}`} style={vis.style}>
                {data.levels[lv]?.split(' (')[0] || lv}
                <small>{data.levels[lv]?.match(/\((.*)\)/)?.[1]}</small>
              </div>

              {hasSpan ? (
                <>
                  <div className="lane-cell empty" />
                  <div className="lane-cell span" style={{ gridColumn: `span ${spanCols}` }}>
                    {lane.throughout.map((p) => (
                      <ProcessCard
                        key={p.id}
                        p={p}
                        active={selected?.id === p.id}
                        onClick={setSelected}
                      />
                    ))}
                  </div>
                </>
              ) : (
                lane.cols.map((procs, i) => (
                  <div key={i} className={`lane-cell ${procs.length ? '' : 'empty'}`}>
                    {procs.map((p) => (
                      <ProcessCard
                        key={p.id}
                        p={p}
                        active={selected?.id === p.id}
                        onClick={setSelected}
                      />
                    ))}
                  </div>
                ))
              )}
            </div>
          );
        })}
      </div>

      {selected && (
        <div className="lifecycle-detail">
          <h3>
            <span style={{ color: 'var(--color-primary)' }}>{selected.code}</span> ·{' '}
            {selected.name}
            {selected.activities.length > 0 && ' — activities in sequence'}
          </h3>
          {selected.description && <p style={{ maxWidth: 800 }}>{selected.description}</p>}
          {selected.activities.length > 0 && (
            <div className="activity-flow">
              {selected.activities.map((a) => (
                <div
                  key={a.id}
                  className="activity-step"
                  onClick={() => navigate(`/?focus=${a.id}`)}
                  style={{ cursor: 'pointer' }}
                  title="Open in the graph"
                >
                  <span className="step-num">{a.sequence}</span>
                  <span className="step-name">{a.name}</span>
                </div>
              ))}
            </div>
          )}
          <div className="admin-actions">
            <button
              className="btn btn-primary btn-sm"
              onClick={() => navigate(`/?focus=${selected.id}`)}
            >
              Open “{selected.code}” in the graph →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
