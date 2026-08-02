import { useEffect, useState } from 'react';
import { api } from '../api/client';

// Each deployment seeds a single framework (selected by FRAMEWORK_KEY), so the
// first framework IS this deployment's framework. Fetch it once and share the
// result across every caller via a module-level promise cache — several
// components (sidebar, page title, guide) need it but only one request should
// go out.
let cache;

export function useDeploymentFramework() {
  const [framework, setFramework] = useState(null);
  useEffect(() => {
    if (!cache) {
      cache = api
        .listFrameworks()
        .then((list) => list?.[0] || null)
        .catch(() => null);
    }
    let alive = true;
    cache.then((fw) => {
      if (alive) setFramework(fw);
    });
    return () => {
      alive = false;
    };
  }, []);
  return framework;
}
