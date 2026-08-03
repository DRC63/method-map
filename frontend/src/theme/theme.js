// Entity-type colours — kept in sync with the CSS custom properties in theme.css.
export const entityColors = {
  process: '#0B2545',
  activity: '#3D5A80',
  role: '#C9A227',
  practice: '#2E7D5B',
  approach: '#8E5BE0',
  product: '#C0392B',
};

// Well-known relationship-code colours (PRINCE2). C/P/N apply to roles/practices/
// approaches; I/O/U/A to products. Any framework code not listed here (e.g. MSP's
// CO/CR/RF/RV/UP/IM, E) is assigned a colour from CODE_PALETTE, so the legend and
// edge colours stay correct for an arbitrary framework's config.codes.
export const codeColors = {
  C: '#A8841C',
  P: '#C9A227',
  N: '#D9C36B',
  I: '#2E7D5B',
  O: '#C0392B',
  U: '#E67E22',
  A: '#8E5BE0',
};

const CODE_PALETTE = ['#C0392B', '#16A085', '#E67E22', '#2980B9', '#9B59B6', '#27AE60', '#34495E', '#E84393'];

// PRINCE2 code groups — fallback when a framework carries no config.codes.
const DEFAULT_CODES = {
  role: { C: 'Responsible', P: 'Participates', N: 'Assists' },
  product: { I: 'Input', O: 'Output', U: 'Update', A: 'Authorise' },
};

export const linkKindColors = {
  contains: 'rgba(120, 130, 145, 0.55)',
  derived: 'rgba(120, 130, 145, 0.20)',
};

export const entityTypeLabels = {
  process: 'Processes',
  activity: 'Activities',
  role: 'Roles',
  practice: 'Practices',
  approach: 'Management Approaches',
  product: 'Products',
};

// The PRINCE2 type catalog, used as a fallback when a framework carries no config
// (keeps the app working if config is ever missing).
const DEFAULT_TYPES = [
  { key: 'process', label: 'Processes', color: entityColors.process, kind: 'container', zone: 'top', order: 1 },
  { key: 'activity', label: 'Activities', color: entityColors.activity, kind: 'hub', zone: 'center', order: 2 },
  { key: 'role', label: 'Management Team Roles', color: entityColors.role, kind: 'node', zone: 'left', order: 3 },
  { key: 'practice', label: 'Practices', color: entityColors.practice, kind: 'node', zone: 'right', order: 4 },
  { key: 'approach', label: 'Management Approaches', color: entityColors.approach, kind: 'node', zone: 'bottom', order: 5 },
  { key: 'product', label: 'Products', color: entityColors.product, kind: 'node', zone: 'below', order: 6 },
];

// Build a per-framework theme from framework.config. Everything the UI needs to
// render an arbitrary framework: type colours, labels, kinds, zones and lanes.
export function makeFrameworkTheme(framework) {
  const cfg = framework?.config || {};
  const types = (cfg.types && cfg.types.length ? cfg.types : DEFAULT_TYPES)
    .slice()
    .sort((a, b) => (a.order || 0) - (b.order || 0));
  const colorMap = Object.fromEntries(types.map((t) => [t.key, t.color]));
  const labelMap = Object.fromEntries(types.map((t) => [t.key, t.label]));

  // Code colours + legend groups, derived from config.codes so the edge legend
  // and link colours are correct for any framework. Known codes keep their
  // colour; unknown ones (e.g. MSP CO/CR/RF/RV/UP/IM/E) draw from CODE_PALETTE.
  const codes = cfg.codes && Object.keys(cfg.codes).length ? cfg.codes : DEFAULT_CODES;
  const frameworkCodeColors = {};
  let paletteIdx = 0;
  const codeGroups = Object.entries(codes).map(([group, mapping]) => ({
    group,
    codes: Object.entries(mapping).map(([code, label]) => {
      if (!frameworkCodeColors[code]) {
        frameworkCodeColors[code] =
          codeColors[code] || CODE_PALETTE[paletteIdx++ % CODE_PALETTE.length];
      }
      return { code, label, color: frameworkCodeColors[code] };
    }),
  }));

  return {
    types,
    lanes: cfg.lanes || [],
    phases: cfg.phases || [],
    // Which layer fills the swimlane cells: 'container' (default) or 'hub' (PMBOK,
    // where the processes themselves grid into KA×Process-Group cells).
    lifecycleLayer: cfg.lifecycle_layer || 'container',
    // Optional map of entity name -> bundled worked-example PDF path (relative to
    // the SPA base). Drives the "View worked example" button in the detail panel.
    examples: cfg.examples || {},
    container: types.find((t) => t.kind === 'container')?.key,
    hub: types.find((t) => t.kind === 'hub')?.key,
    nodeTypes: types.filter((t) => t.kind === 'node'),
    typesInZone: (z) => types.filter((t) => t.kind === 'node' && t.zone === z),
    colorOf: (t) => colorMap[t] || entityColors[t] || '#888',
    labelOf: (t) => labelMap[t] || entityTypeLabels[t] || t,
    codeColors: frameworkCodeColors,
    codeGroups,
  };
}
