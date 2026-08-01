// Fixed "matrix / swimlane" layout for the Method Explorer.
//
//                         PROCESSES  (top row)
//                         ACTIVITIES (stacked under their process)
//   MANAGEMENT                                          PRACTICES
//   TEAM ROLES            PRODUCTS   (band below)       (right)
//   (left)
//                    MANAGEMENT APPROACHES (bottom row)
//
// Activities are the central hub: processes sit above them, products below,
// roles to the left, practices to the right, approaches along the bottom.
// Zone labels are horizontal, colour-coded to their entity type, and sit in the
// clear gaps between the node bands.
// Returns { pos: Map(id -> {x, y}), zones: [{label, x, y, color}] }.
import { entityColors } from './theme';

const COL = 280; // horizontal gap between process columns
const ACT_TOP = -470; // y of the first activity under a process
const ROW = 66; // vertical gap between stacked activities
const PROCESS_Y = -690;
const PROD_GAP = 215; // clear gap between deepest activity and the products band
const SIDE_GAP = 380; // gap from the activity block to the role/practice columns
const RGAP = 100; // vertical gap between roles / practices
const PROD_PER_ROW = 7;
const PCOL = 210;
const PROW = 72;
const AGAP = 230; // horizontal gap between approaches

const bySort = (arr) =>
  [...arr].sort(
    (a, b) => (a.sort_order || 0) - (b.sort_order || 0) || a.name.localeCompare(b.name),
  );

export function computeStructuredLayout(nodes) {
  const pos = new Map();
  const by = (t) => nodes.filter((n) => n.type === t);

  // --- processes across the top ---
  const processes = bySort(by('process'));
  const totalW = Math.max(0, processes.length - 1) * COL;
  const leftEdge = -totalW / 2;
  const procX = new Map();
  processes.forEach((p, i) => {
    const x = leftEdge + i * COL;
    procX.set(p.id, x);
    pos.set(p.id, { x, y: PROCESS_Y });
  });

  // --- activities stacked beneath their owning process ---
  const activities = by('activity');
  const groups = new Map();
  activities.forEach((a) => {
    const k = a.parent_id ?? '__none__';
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(a);
  });
  let maxRows = 1;
  groups.forEach((arr) => (maxRows = Math.max(maxRows, arr.length)));
  let orphanCol = 0;
  groups.forEach((arr, procId) => {
    const x = procX.has(procId) ? procX.get(procId) : leftEdge + orphanCol++ * COL;
    bySort(arr).forEach((a, j) => pos.set(a.id, { x, y: ACT_TOP + j * ROW }));
  });

  // --- products band below the activities ---
  const lastActY = ACT_TOP + (maxRows - 1) * ROW;
  const products = bySort(by('product'));
  const prodTop = lastActY + PROD_GAP;
  const per = Math.min(PROD_PER_ROW, Math.max(1, products.length));
  products.forEach((p, k) => {
    const row = Math.floor(k / per);
    const col = k % per;
    const inRow = Math.min(per, products.length - row * per);
    const rowW = (inRow - 1) * PCOL;
    pos.set(p.id, { x: -rowW / 2 + col * PCOL, y: prodTop + row * PROW });
  });
  const prodRows = Math.max(1, Math.ceil(products.length / per));
  const spineBottom = prodTop + (prodRows - 1) * PROW;

  // --- roles left, practices right, centred on the spine ---
  const midY = (PROCESS_Y + spineBottom) / 2;
  const leftX = leftEdge - SIDE_GAP;
  const rightX = leftEdge + totalW + SIDE_GAP;
  const colY = (arr, i) => midY - ((arr.length - 1) / 2) * RGAP + i * RGAP;

  const roles = bySort(by('role'));
  roles.forEach((r, i) => pos.set(r.id, { x: leftX, y: colY(roles, i) }));
  const practices = bySort(by('practice'));
  practices.forEach((r, i) => pos.set(r.id, { x: rightX, y: colY(practices, i) }));

  // --- management approaches along the bottom ---
  const approaches = bySort(by('approach'));
  const aW = Math.max(0, approaches.length - 1) * AGAP;
  const bottomY = spineBottom + 165;
  approaches.forEach((a, i) => pos.set(a.id, { x: -aW / 2 + i * AGAP, y: bottomY }));

  // --- zone labels (all horizontal, colour-coded, in the clear band gaps) ---
  const zones = [
    { label: 'PROCESSES', x: 0, y: PROCESS_Y - 110, color: entityColors.process },
    // in the clear lane between the process row and the activity rows
    { label: 'ACTIVITIES', x: 0, y: ACT_TOP - 100, color: entityColors.activity },
    // in the clear lane between the deepest activity and the products band
    { label: 'PRODUCTS', x: 0, y: lastActY + PROD_GAP * 0.5, color: entityColors.product },
    // top header band, flanking PROCESSES (their columns sit below, colour-linked)
    { label: 'MANAGEMENT TEAM ROLES', x: leftX, y: PROCESS_Y - 110, color: entityColors.role },
    { label: 'PRACTICES', x: rightX, y: PROCESS_Y - 110, color: entityColors.practice },
    { label: 'MANAGEMENT APPROACHES', x: 0, y: bottomY + 130, color: entityColors.approach },
  ];

  return { pos, zones };
}

// ---------------------------------------------------------------------------
// Timeline layout — echoes the Project Lifecycle view. Processes sit in three
// swimlanes (Directing / Managing / Delivering) laid out left->right in
// lifecycle sequence; each process's activities stack in its time-column just
// below; roles / practices / approaches / products form static resource bands
// underneath (they light up as the scrubber passes the stages that use them).
// ---------------------------------------------------------------------------
const TCOL = 300; // time-column spacing between processes
const LANE_Y = { directing: -720, managing: -600, delivering: -480 };
const T_ACT_TOP = -360;
const T_AROW = 58;
const BAND_GAP = 135;

export function computeTimelineLayout(nodes) {
  const pos = new Map();
  const by = (t) => nodes.filter((n) => n.type === t);
  const bySeq = (arr) =>
    [...arr].sort(
      (a, b) => (a.sequence ?? a.sort_order ?? 0) - (b.sequence ?? b.sort_order ?? 0),
    );

  const processes = bySeq(by('process'));
  const totalW = Math.max(0, processes.length - 1) * TCOL;
  const leftEdge = -totalW / 2;

  // --- process swimlanes, ordered by lifecycle sequence ---
  const procX = new Map();
  processes.forEach((p, i) => {
    const x = leftEdge + i * TCOL;
    procX.set(p.id, x);
    pos.set(p.id, { x, y: LANE_Y[p.lifecycle_level] ?? LANE_Y.managing });
  });

  // --- activities stacked under their process's time-column ---
  const groups = new Map();
  by('activity').forEach((a) => {
    const k = a.parent_id ?? '__none__';
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(a);
  });
  let maxRows = 1;
  groups.forEach((arr) => (maxRows = Math.max(maxRows, arr.length)));
  let orphan = 0;
  groups.forEach((arr, pid) => {
    const x = procX.has(pid) ? procX.get(pid) : leftEdge + orphan++ * TCOL;
    [...arr]
      .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
      .forEach((a, j) => pos.set(a.id, { x, y: T_ACT_TOP + j * T_AROW }));
  });
  const actBottom = T_ACT_TOP + (maxRows - 1) * T_AROW;

  // --- static resource bands below (spread across the timeline width) ---
  const placeBand = (items, yStart, perRow, rowGap) => {
    const sorted = bySort(items);
    sorted.forEach((e, k) => {
      const row = Math.floor(k / perRow);
      const col = k % perRow;
      const inRow = Math.min(perRow, sorted.length - row * perRow);
      const step = inRow > 1 ? totalW / (inRow - 1) : 0;
      const x = inRow > 1 ? -totalW / 2 + col * step : 0;
      pos.set(e.id, { x, y: yStart + row * rowGap });
    });
    const rows = Math.max(1, Math.ceil(sorted.length / perRow));
    return { top: yStart, mid: yStart + ((rows - 1) * rowGap) / 2, bottom: yStart + (rows - 1) * rowGap };
  };

  let y = actBottom + 170;
  const products = placeBand(by('product'), y, 10, 66);
  y = products.bottom + BAND_GAP;
  const roles = placeBand(by('role'), y, 12, 66);
  y = roles.bottom + BAND_GAP;
  const practices = placeBand(by('practice'), y, 12, 66);
  y = practices.bottom + BAND_GAP;
  const approaches = placeBand(by('approach'), y, 12, 66);

  // --- zone labels: swimlane names + resource band names on the left rail ---
  const railX = leftEdge - 260;
  const zones = [
    { label: 'DIRECTING', x: railX, y: LANE_Y.directing, color: entityColors.process, scale: 0.62 },
    { label: 'MANAGING', x: railX, y: LANE_Y.managing, color: entityColors.process, scale: 0.62 },
    { label: 'DELIVERING', x: railX, y: LANE_Y.delivering, color: entityColors.process, scale: 0.62 },
    { label: 'ACTIVITIES', x: railX, y: (T_ACT_TOP + actBottom) / 2, color: entityColors.activity, scale: 0.85 },
    { label: 'PRODUCTS', x: railX, y: products.mid, color: entityColors.product, scale: 0.85 },
    { label: 'ROLES', x: railX, y: roles.mid, color: entityColors.role, scale: 0.85 },
    { label: 'PRACTICES', x: railX, y: practices.mid, color: entityColors.practice, scale: 0.85 },
    { label: 'APPROACHES', x: railX, y: approaches.mid, color: entityColors.approach, scale: 0.85 },
  ];

  // phase headers above the process columns
  const PHASE_LABEL = {
    'pre-project': 'Pre-project',
    initiation: 'Initiation',
    delivery: 'Delivery ⟳',
    final: 'Final',
  };
  const phaseGroups = new Map();
  processes.forEach((p) => {
    if (PHASE_LABEL[p.lifecycle_phase]) {
      if (!phaseGroups.has(p.lifecycle_phase)) phaseGroups.set(p.lifecycle_phase, []);
      phaseGroups.get(p.lifecycle_phase).push(procX.get(p.id));
    }
  });
  phaseGroups.forEach((xs, ph) => {
    const x = xs.reduce((a, b) => a + b, 0) / xs.length;
    zones.push({
      label: PHASE_LABEL[ph],
      x,
      y: LANE_Y.directing - 130,
      color: 'rgba(11,37,69,0.5)',
      scale: 0.62,
    });
  });

  return { pos, zones };
}
