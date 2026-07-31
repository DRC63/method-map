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
