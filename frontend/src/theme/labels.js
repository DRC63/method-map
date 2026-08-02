// The lifecycle noun is framework-specific: PRINCE2 governs a *project*, MSP a
// *programme* (AXELOS British spelling — matches the rest of the MSP data, which
// uses "Programme" throughout). Prefer an explicit config override if a framework
// sets one; otherwise infer from the framework name/key so no reseed is needed.
export function lifecycleNoun(fw) {
  if (fw?.config?.lifecycle_noun) return fw.config.lifecycle_noun;
  const s = `${fw?.name || ''} ${fw?.key || ''}`.toLowerCase();
  return /msp|programme/.test(s) ? 'programme' : 'project';
}

export function lifecycleLabel(fw) {
  if (fw?.config?.lifecycle_label) return fw.config.lifecycle_label;
  const noun = lifecycleNoun(fw);
  return `${noun.charAt(0).toUpperCase()}${noun.slice(1)} Lifecycle`;
}
