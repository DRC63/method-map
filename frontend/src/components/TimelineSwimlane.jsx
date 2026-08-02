import { Fragment, useMemo } from 'react';

// The Explorer "Timeline" view as a CSS swimlane grid (lanes × stage columns)
// instead of a force-graph. Processes sit in their (lane, stage) cell with their
// activities beneath; the node-type layers form static resource bands below.
// Everything is framework-driven from `theme` (lanes/phases/types), so it works
// for PRINCE2 and MSP alike. The timeline scrubber drives `timelineSet`: when it
// is non-null, members are lit and non-members dim — same semantics as the old
// canvas timeline, now in the DOM.
export default function TimelineSwimlane({ data, theme, selectedId, onSelectNode, timelineSet }) {
  const lanes = theme?.lanes || [];
  const phaseCols = useMemo(
    () => (theme?.phases || []).filter((p) => p.column),
    [theme],
  );
  const deliveryKey = useMemo(
    () =>
      phaseCols.find((c) => c.key === 'delivery')?.key ||
      phaseCols[phaseCols.length - 1]?.key,
    [phaseCols],
  );
  const columnOf = useMemo(() => {
    const keys = new Set(phaseCols.map((c) => c.key));
    return (phase) => (keys.has(phase) ? phase : deliveryKey);
  }, [phaseCols, deliveryKey]);

  const containerType = theme?.container;
  const hubType = theme?.hub;
  const nodes = data?.nodes || [];

  const processes = useMemo(
    () =>
      nodes
        .filter((n) => n.type === containerType)
        .sort(
          (a, b) =>
            (a.sequence ?? a.sort_order ?? 0) - (b.sequence ?? b.sort_order ?? 0),
        ),
    [nodes, containerType],
  );

  const actsByProc = useMemo(() => {
    const m = new Map();
    nodes.forEach((n) => {
      if (n.type === hubType && n.parent_id != null) {
        if (!m.has(n.parent_id)) m.set(n.parent_id, []);
        m.get(n.parent_id).push(n);
      }
    });
    for (const arr of m.values())
      arr.sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0));
    return m;
  }, [nodes, hubType]);

  const resourceBands = useMemo(
    () =>
      (theme?.nodeTypes || [])
        .map((t) => ({ type: t, items: nodes.filter((n) => n.type === t.key) }))
        .filter((b) => b.items.length),
    [nodes, theme],
  );

  const cellMap = useMemo(() => {
    const m = new Map();
    processes.forEach((p) => {
      const li = lanes.findIndex((l) => l.key === p.lifecycle_level);
      const ci = phaseCols.findIndex((c) => c.key === columnOf(p.lifecycle_phase));
      if (li < 0 || ci < 0) return;
      const key = `${li}:${ci}`;
      if (!m.has(key)) m.set(key, []);
      m.get(key).push(p);
    });
    return m;
  }, [processes, lanes, phaseCols, columnOf]);

  const isDim = (id) => (timelineSet ? !timelineSet.has(id) : false);
  const stateClass = (id) =>
    selectedId === id ? 'tl-sel' : isDim(id) ? 'tl-dim' : '';
  const laneShort = (l) => l.label.replace(/\s*\(.*$/, '');
  const laneGloss = (l) => l.label.match(/\(([^)]*)\)/)?.[1] || '';

  if (!processes.length) {
    return <div className="graph-empty">No processes in the selected layers.</div>;
  }

  return (
    <div className="tl-swim">
      <div
        className="tl-grid"
        style={{ gridTemplateColumns: `168px repeat(${phaseCols.length}, minmax(180px, 1fr))` }}
      >
        <div className="tl-corner">time&nbsp;&rarr;</div>
        {phaseCols.map((c) => (
          <div key={c.key} className="tl-colhead">{c.header || c.label}</div>
        ))}

        {lanes.map((lane, li) => (
          <Fragment key={lane.key}>
            <div className={`tl-lanehead tl-lane-${li}`}>
              {laneShort(lane)}
              {laneGloss(lane) && <small>{laneGloss(lane)}</small>}
            </div>
            {phaseCols.map((col, ci) => (
              <div key={col.key} className="tl-cell">
                {(cellMap.get(`${li}:${ci}`) || []).map((p) => {
                  const acts = actsByProc.get(p.id) || [];
                  return (
                    <div
                      key={p.id}
                      className={`tl-proc ${stateClass(p.id)}`}
                      onClick={() => onSelectNode(p.id)}
                      title={p.name}
                    >
                      <div className="tl-proc-head">
                        {p.code && <span className="tl-proc-code">{p.code}</span>}
                        <span className="tl-proc-name">{p.name}</span>
                      </div>
                      {acts.length > 0 && (
                        <div className="tl-acts">
                          {acts.map((a) => (
                            <button
                              key={a.id}
                              className={`tl-act ${stateClass(a.id)}`}
                              style={{ background: theme.colorOf(hubType) }}
                              onClick={(e) => {
                                e.stopPropagation();
                                onSelectNode(a.id);
                              }}
                              title={a.name}
                            />
                          ))}
                          <span className="tl-acts-count">{acts.length}</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </Fragment>
        ))}
      </div>

      <div className="tl-bands">
        {resourceBands.map(({ type, items }) => (
          <div key={type.key} className="tl-band">
            <div className="tl-band-label" style={{ background: theme.colorOf(type.key) }}>
              {type.label}
              <span className="tl-band-count">{items.length}</span>
            </div>
            <div className="tl-chips">
              {items.map((n) => (
                <button
                  key={n.id}
                  className={`tl-chip ${stateClass(n.id)}`}
                  style={{ '--chip': theme.colorOf(type.key) }}
                  onClick={() => onSelectNode(n.id)}
                  title={n.name}
                >
                  {n.name}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
