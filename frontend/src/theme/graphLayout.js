// Fixed "matrix / swimlane" and "timeline" layouts for the Method Explorer.
//
// Both are driven by the framework theme (theme.types with kind + zone, and
// theme.lanes) rather than hardcoded PRINCE2 types, so any framework lays out.
//   kind:  container (top row) · hub (stacked under container) · node (a target)
//   zone:  where a node type sits in the Matrix — below / left / right / bottom
// Returns { pos: Map(id -> {x, y}), zones: [{label, x, y, color, scale?}] }.

const COL = 280;
const ACT_TOP = -470;
const ROW = 66;
const PROCESS_Y = -690;
const PROD_GAP = 215;
const SIDE_GAP = 380;
const RGAP = 100;
const PER_ROW = 7;
const PCOL = 210;
const PROW = 72;
const AGAP = 230;

const bySort = (arr) =>
  [...arr].sort(
    (a, b) => (a.sort_order || 0) - (b.sort_order || 0) || a.name.localeCompare(b.name),
  );

export function computeStructuredLayout(nodes, theme) {
  const pos = new Map();
  const by = (t) => nodes.filter((n) => n.type === t);
  const { container, hub, colorOf, labelOf } = theme;
  const UP = (t) => labelOf(t).toUpperCase();
  const zones = [];

  // --- container row across the top ---
  const containers = bySort(by(container));
  const totalW = Math.max(0, containers.length - 1) * COL;
  const leftEdge = -totalW / 2;
  const cx = new Map();
  containers.forEach((p, i) => {
    const x = leftEdge + i * COL;
    cx.set(p.id, x);
    pos.set(p.id, { x, y: PROCESS_Y });
  });
  zones.push({ label: UP(container), x: 0, y: PROCESS_Y - 110, color: colorOf(container) });

  // --- hubs stacked beneath their container ---
  const groups = new Map();
  by(hub).forEach((a) => {
    const k = a.parent_id ?? '__none__';
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(a);
  });
  let maxRows = 1;
  groups.forEach((arr) => (maxRows = Math.max(maxRows, arr.length)));
  let orphan = 0;
  groups.forEach((arr, pid) => {
    const x = cx.has(pid) ? cx.get(pid) : leftEdge + orphan++ * COL;
    bySort(arr).forEach((a, j) => pos.set(a.id, { x, y: ACT_TOP + j * ROW }));
  });
  const lastActY = ACT_TOP + (maxRows - 1) * ROW;
  zones.push({ label: UP(hub), x: 0, y: ACT_TOP - 100, color: colorOf(hub) });

  // --- 'below' zone: bands under the hubs (products) ---
  let top = lastActY + PROD_GAP;
  let spineBottom = top;
  theme.typesInZone('below').forEach((td, ti) => {
    if (ti > 0) top += 90;
    const items = bySort(by(td.key));
    const per = Math.min(PER_ROW, Math.max(1, items.length));
    items.forEach((p, k) => {
      const row = Math.floor(k / per);
      const col = k % per;
      const inRow = Math.min(per, items.length - row * per);
      pos.set(p.id, { x: -((inRow - 1) * PCOL) / 2 + col * PCOL, y: top + row * PROW });
    });
    const rows = Math.max(1, Math.ceil(items.length / per));
    const bandBottom = top + (rows - 1) * PROW;
    // Label sits above the band by default; a type can set `label_below: true`
    // (e.g. PMBOK's Tools & Techniques) to place its heading under its nodes.
    const labelY = td.label_below ? bandBottom + PROD_GAP * 0.5 : top - PROD_GAP * 0.5;
    zones.push({ label: UP(td.key), x: 0, y: labelY, color: colorOf(td.key) });
    top = bandBottom;
    spineBottom = top;
  });

  // --- 'left' / 'right' zones: columns flanking the spine ---
  const midY = (PROCESS_Y + spineBottom) / 2;
  const colY = (arr, i) => midY - ((arr.length - 1) / 2) * RGAP + i * RGAP;
  theme.typesInZone('left').forEach((td, ci) => {
    const x = leftEdge - SIDE_GAP - ci * SIDE_GAP;
    const items = bySort(by(td.key));
    items.forEach((r, i) => pos.set(r.id, { x, y: colY(items, i) }));
    zones.push({ label: UP(td.key), x, y: PROCESS_Y - 110, color: colorOf(td.key) });
  });
  theme.typesInZone('right').forEach((td, ci) => {
    const x = leftEdge + totalW + SIDE_GAP + ci * SIDE_GAP;
    const items = bySort(by(td.key));
    items.forEach((r, i) => pos.set(r.id, { x, y: colY(items, i) }));
    zones.push({ label: UP(td.key), x, y: PROCESS_Y - 110, color: colorOf(td.key) });
  });

  // --- 'bottom' zone: rows along the bottom ---
  let bottomY = spineBottom + 165;
  theme.typesInZone('bottom').forEach((td) => {
    const items = bySort(by(td.key));
    const aW = Math.max(0, items.length - 1) * AGAP;
    items.forEach((a, i) => pos.set(a.id, { x: -aW / 2 + i * AGAP, y: bottomY }));
    zones.push({ label: UP(td.key), x: 0, y: bottomY + 130, color: colorOf(td.key) });
    bottomY += 165;
  });

  return { pos, zones };
}

// ---------------------------------------------------------------------------
// Timeline layout — echoes the Project Lifecycle: containers in swimlanes (from
// theme.lanes) laid left->right by sequence; hubs stack in each column; node
// types form static resource bands below.
// ---------------------------------------------------------------------------
const TCOL = 300;
const T_ACT_TOP = -360;
const T_AROW = 58;
const BAND_GAP = 135;

export function computeTimelineLayout(nodes, theme) {
  const pos = new Map();
  const by = (t) => nodes.filter((n) => n.type === t);
  const bySeq = (arr) =>
    [...arr].sort(
      (a, b) => (a.sequence ?? a.sort_order ?? 0) - (b.sequence ?? b.sort_order ?? 0),
    );
  const { container, hub, colorOf, labelOf } = theme;
  const UP = (t) => labelOf(t).toUpperCase();

  // swimlane y for each lane (evenly spaced, top = first lane)
  const lanes = theme.lanes.length ? theme.lanes : [{ key: 'managing', label: '' }];
  const LANE_TOP = -720;
  const LANE_STEP = 120;
  const laneY = {};
  lanes.forEach((l, i) => (laneY[l.key] = LANE_TOP + i * LANE_STEP));
  const defaultLane = lanes[Math.floor(lanes.length / 2)]?.key;

  const containers = bySeq(by(container));
  const totalW = Math.max(0, containers.length - 1) * TCOL;
  const leftEdge = -totalW / 2;
  const cx = new Map();
  containers.forEach((p, i) => {
    const x = leftEdge + i * TCOL;
    cx.set(p.id, x);
    pos.set(p.id, { x, y: laneY[p.lifecycle_level] ?? laneY[defaultLane] });
  });

  // hubs stacked under their container's column
  const groups = new Map();
  by(hub).forEach((a) => {
    const k = a.parent_id ?? '__none__';
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(a);
  });
  let maxRows = 1;
  groups.forEach((arr) => (maxRows = Math.max(maxRows, arr.length)));
  let orphan = 0;
  groups.forEach((arr, pid) => {
    const x = cx.has(pid) ? cx.get(pid) : leftEdge + orphan++ * TCOL;
    bySort(arr).forEach((a, j) => pos.set(a.id, { x, y: T_ACT_TOP + j * T_AROW }));
  });
  const actBottom = T_ACT_TOP + (maxRows - 1) * T_AROW;

  // resource bands (every node type, in order) spread across the width
  const placeBand = (items, yStart, perRow, rowGap) => {
    const sorted = bySort(items);
    sorted.forEach((e, k) => {
      const row = Math.floor(k / perRow);
      const col = k % perRow;
      const inRow = Math.min(perRow, sorted.length - row * perRow);
      const step = inRow > 1 ? totalW / (inRow - 1) : 0;
      pos.set(e.id, { x: inRow > 1 ? -totalW / 2 + col * step : 0, y: yStart + row * rowGap });
    });
    const rows = Math.max(1, Math.ceil(sorted.length / perRow));
    return { mid: yStart + ((rows - 1) * rowGap) / 2, bottom: yStart + (rows - 1) * rowGap };
  };

  const railX = leftEdge - 260;
  const zones = lanes.map((l) => ({
    label: l.label.split(' (')[0].toUpperCase(),
    x: railX,
    y: laneY[l.key],
    color: colorOf(container),
    scale: 0.62,
  }));
  zones.push({ label: UP(hub), x: railX, y: (T_ACT_TOP + actBottom) / 2, color: colorOf(hub), scale: 0.85 });

  let y = actBottom + 170;
  theme.nodeTypes.forEach((td, i) => {
    if (i > 0) y += BAND_GAP;
    const band = placeBand(by(td.key), y, 12, 66);
    zones.push({ label: UP(td.key), x: railX, y: band.mid, color: colorOf(td.key), scale: 0.85 });
    y = band.bottom;
  });

  // phase headers above the columns (phases flagged column:true in the config)
  const headerPhases = theme.phases.filter((p) => p.column);
  const phaseGroups = new Map();
  containers.forEach((p) => {
    if (headerPhases.some((hp) => hp.key === p.lifecycle_phase)) {
      if (!phaseGroups.has(p.lifecycle_phase)) phaseGroups.set(p.lifecycle_phase, []);
      phaseGroups.get(p.lifecycle_phase).push(cx.get(p.id));
    }
  });
  phaseGroups.forEach((xs, ph) => {
    const label = headerPhases.find((hp) => hp.key === ph)?.header || ph;
    zones.push({
      label,
      x: xs.reduce((a, b) => a + b, 0) / xs.length,
      y: LANE_TOP - 130,
      color: 'rgba(11,37,69,0.5)',
      scale: 0.62,
    });
  });

  return { pos, zones };
}
