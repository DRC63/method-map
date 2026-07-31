const BASE = '/api';

// Admin password (for authoring mode) is held in localStorage and sent as a
// header on write requests. Read requests never need it.
const PW_KEY = 'methodmap.adminPassword';

export function getAdminPassword() {
  return localStorage.getItem(PW_KEY) || '';
}
export function setAdminPassword(pw) {
  if (pw) localStorage.setItem(PW_KEY, pw);
  else localStorage.removeItem(PW_KEY);
}

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (options.admin) headers['X-Admin-Password'] = getAdminPassword();
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${options.method || 'GET'} ${path} failed (${res.status}): ${body}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

const get = (path) => request(path);
const post = (path, data, admin = false) =>
  request(path, { method: 'POST', body: JSON.stringify(data), admin });
const put = (path, data, admin = false) =>
  request(path, { method: 'PUT', body: JSON.stringify(data), admin });
const del = (path, admin = false) => request(path, { method: 'DELETE', admin });

export const api = {
  getMeta: () => get('/meta'),
  verifyPassword: (password) => post('/auth/verify', { password }),

  listFrameworks: () => get('/frameworks'),
  getFramework: (key) => get(`/frameworks/${key}`),
  listEntities: (key, params = {}) => get(`/frameworks/${key}/entities${qs(params)}`),
  listRelationships: (key) => get(`/frameworks/${key}/relationships`),
  getGraph: (key, { types, derived } = {}) =>
    get(`/frameworks/${key}/graph${qs({ types, derived })}`),
  getLifecycle: (key) => get(`/frameworks/${key}/lifecycle`),
  getEntity: (id) => get(`/entities/${id}`),

  // authoring (admin password required)
  createEntity: (data) => post('/entities', data, true),
  updateEntity: (id, data) => put(`/entities/${id}`, data, true),
  deleteEntity: (id) => del(`/entities/${id}`, true),
  createRelationship: (data) => post('/relationships', data, true),
  updateRelationship: (id, data) => put(`/relationships/${id}`, data, true),
  deleteRelationship: (id) => del(`/relationships/${id}`, true),

  // export URLs (used as hrefs / window.open)
  csvUrl: (key, focusId) => `${BASE}/frameworks/${key}/export.csv${qs({ focus_entity_id: focusId })}`,
  xlsxUrl: (key, focusId) => `${BASE}/frameworks/${key}/export.xlsx${qs({ focus_entity_id: focusId })}`,
  pdfUrl: (key, entityId) => `${BASE}/frameworks/${key}/entities/${entityId}/report.pdf`,
};

function qs(params) {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null && v !== '',
  );
  if (!entries.length) return '';
  return `?${new URLSearchParams(entries).toString()}`;
}
