// Entity-type colours — kept in sync with the CSS custom properties in theme.css.
export const entityColors = {
  process: '#0B2545',
  activity: '#3D5A80',
  role: '#C9A227',
  practice: '#2E7D5B',
  approach: '#8E5BE0',
  product: '#C0392B',
};

// Relationship-code colours. C/P/N apply to roles/practices/approaches;
// I/O/U/A apply to products.
export const codeColors = {
  C: '#A8841C',
  P: '#C9A227',
  N: '#D9C36B',
  I: '#2E7D5B',
  O: '#C0392B',
  U: '#E67E22',
  A: '#8E5BE0',
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
