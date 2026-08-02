import { makeFrameworkTheme } from '../theme/theme';
import { useDeploymentFramework } from '../lib/useDeploymentFramework';
import { lifecycleLabel, lifecycleNoun } from '../theme/labels';

// Join a list into "A, B and C".
function andList(arr) {
  const a = arr.filter(Boolean);
  if (a.length <= 1) return a[0] || '';
  return `${a.slice(0, -1).join(', ')} and ${a[a.length - 1]}`;
}

// Prose that genuinely differs by framework — the sourcing/accuracy note and the
// short name for the time-ordered process model. Everything else on this page is
// derived from the framework's own config, so a new framework needs no code here.
// Every live framework, in one place. The Guide's "related" note is generated
// from this, so adding a framework is a single-line change here (not an edit to
// each entry's cross-links). key = framework key; slug = front-door path.
const APPS = [
  { key: 'prince2-7', slug: 'prince2', label: 'PRINCE2 7', kind: 'projects' },
  { key: 'msp-5', slug: 'msp', label: 'Managing Successful Programmes (MSP)', kind: 'programmes' },
  { key: 'safe-essential', slug: 'safe', label: 'SAFe® 6.0 Essential', kind: 'scaled agile' },
  { key: 'pmbok-6', slug: 'pmbok', label: 'the PMBOK® Guide (6th ed.)', kind: 'the PMI process standard' },
];

// "This is one of several frameworks … PRINCE2 for projects (open →), MSP for
// programmes (open →) and …" — every framework except the current one, linked to
// its own front-door app.
function relatedNote(currentKey) {
  const others = APPS.filter((a) => a.key !== currentKey);
  if (!others.length) return null;
  return (
    <>
      This is one of several frameworks the Method Map holds side by side, each as its own
      map:{' '}
      {others.map((a, i) => (
        <span key={a.slug}>
          {i > 0 ? (i === others.length - 1 ? ' and ' : ', ') : ''}
          <strong>{a.label}</strong> for {a.kind} (
          <a href={`https://apps.p3mai.com/${a.slug}/`}>open →</a>)
        </span>
      ))}
      .
    </>
  );
}

const FRAMEWORK_PROSE = {
  'prince2-7': {
    modelName: 'the classic PRINCE2 process model',
    accuracy: (
      <>
        Process, role, practice, approach and product <em>names</em> are corroborated
        across public sources. The activity-level breakdown and its codes are a
        best-effort reconstruction (from prince2.wiki, CC-BY 4.0) and are shown with a
        dashed{' '}
        <span className="confidence-flag confidence-indicative">◌ indicative</span> marker.
        Verify against the licensed PRINCE2 manual before using any of this as formal
        audit, training or certification evidence.
      </>
    ),
    related: relatedNote('prince2-7'),
  },
  'msp-5': {
    modelName: 'the MSP transformational flow',
    accuracy: (
      <>
        Programme process, role, theme, product and principle <em>names</em> follow MSP
        5th edition (<em>Managing Successful Programmes</em>, 2020). The activity-level
        breakdown and every cross-reference mark are an <strong>indicative</strong>,
        best-effort reconstruction — shown with a dashed{' '}
        <span className="confidence-flag confidence-indicative">◌ indicative</span> marker —
        and must be SME-verified against the licensed MSP manual before use as formal
        audit, training or certification evidence.
      </>
    ),
    related: relatedNote('msp-5'),
  },
  'safe-essential': {
    modelName: 'the SAFe PI (Program Increment) cadence',
    accuracy: (
      <>
        Event, role, artifact, competency and principle <em>names</em> follow SAFe 6.0
        Essential. The activity breakdown of each event and every cross-reference mark
        are an <strong>indicative</strong>, best-effort reconstruction — shown with a
        dashed{' '}
        <span className="confidence-flag confidence-indicative">◌ indicative</span> marker —
        and must be SME-verified against the licensed SAFe body of knowledge before use as
        formal audit, training or certification evidence. SAFe&reg; and Scaled Agile
        Framework&reg; are trademarks of Scaled Agile, Inc.; this is an independent
        reference tool, not affiliated with or endorsed by Scaled Agile, Inc.
      </>
    ),
    related: relatedNote('safe-essential'),
  },
  'pmbok-6': {
    modelName: 'the PMBOK process matrix (5 Process Groups × 10 Knowledge Areas)',
    accuracy: (
      <>
        The Process Group, Knowledge Area and process <em>names</em>, and each process's
        placement in the 5×10 matrix, follow the PMBOK<span>&reg;</span> Guide 6th edition
        and are corroborated across public sources. The <strong>ITTO</strong>{' '}
        cross-references (Inputs, Tools &amp; Techniques and Outputs per process) are a
        curated, <strong>indicative</strong> reconstruction — the most characteristic items
        per process, not the guide's exhaustive tables — shown with a dashed{' '}
        <span className="confidence-flag confidence-indicative">◌ indicative</span> marker,
        and must be SME-verified against the licensed PMBOK Guide before use as formal
        audit, training or certification evidence. PMBOK, PMI and PMP are marks of the
        Project Management Institute, Inc.; this is an independent reference tool, not
        affiliated with or endorsed by PMI.
      </>
    ),
    related: relatedNote('pmbok-6'),
  },
};

export default function Guide() {
  const fw = useDeploymentFramework();
  if (!fw) {
    return (
      <div className="prose">
        <div className="card">Loading…</div>
      </div>
    );
  }

  const theme = makeFrameworkTheme(fw);
  const noun = lifecycleNoun(fw);
  const counts = fw.entity_counts || {};
  const prose = FRAMEWORK_PROSE[fw.key] || {
    modelName: `the ${fw.name} process model`,
    accuracy: fw.description,
  };

  // Time-ordered lifecycle flow + swimlanes, straight from config.
  const phaseFlow = theme.phases
    .filter((p) => p.column)
    .map((p) => p.header || p.label)
    .join(' → ');
  const laneShort = theme.lanes.map((l) => l.label.replace(/\s*\(.*$/, ''));

  // Which layers each edge-code group labels (roles group may cover several types).
  const layersForGroup = (group) =>
    theme.types.filter((t) => t.code_group === group).map((t) => theme.labelOf(t.key));

  const nodeLayerLabels = theme.nodeTypes.map((t) => t.label);

  return (
    <div className="prose">
      <div className="card section-gap">
        <h2 style={{ marginTop: 0 }}>What this is</h2>
        <p className="muted" style={{ marginTop: -4 }}>
          {fw.name}
          {fw.edition ? ` · ${fw.edition}` : ''}
        </p>
        <p>
          The Method Map turns {fw.name} into an interactive network. Every management{' '}
          <strong>activity</strong> is cross-referenced to the {andList(nodeLayerLabels)}{' '}
          that surround it. Explore how any one element connects to the rest of the
          method — useful when tailoring a {noun}, onboarding a team, or explaining
          governance to a client.
        </p>
      </div>

      <div className="card section-gap">
        <h2 style={{ marginTop: 0 }}>Two ways to look at it</h2>
        <ul className="bullets">
          <li>
            <strong>Method Explorer</strong> — the interdependency network. Best for
            &ldquo;what connects to what&rdquo;: pick any element and trace its links
            across the whole method.
          </li>
          <li>
            <strong>{lifecycleLabel(fw)}</strong> — the same processes laid out in time.{' '}
            {prose.modelName.charAt(0).toUpperCase() + prose.modelName.slice(1)}: time
            runs left→right ({phaseFlow}) across {laneShort.length} swimlanes (
            {laneShort.join(' / ')}). Click a process to see its activities in sequence.
          </li>
        </ul>
      </div>

      <div className="card section-gap">
        <h2 style={{ marginTop: 0 }}>The layers</h2>
        <div style={{ display: 'grid', gap: 8 }}>
          {theme.types.map((t) => (
            <div key={t.key} className="legend-item" style={{ fontSize: '0.95rem' }}>
              <span className="layer-swatch" style={{ background: theme.colorOf(t.key) }} />
              <strong style={{ color: 'var(--color-text)' }}>{theme.labelOf(t.key)}</strong>
              {typeof counts[t.key] === 'number' && (
                <span className="muted">&nbsp;({counts[t.key]})</span>
              )}
            </div>
          ))}
        </div>
        <p style={{ marginTop: 12 }}>
          Toggle any layer on or off in the Explorer. With <em>Activities</em> hidden,
          the map shows <strong>indirect links</strong> — two elements are connected
          when they co-occur on the same activity (e.g. which Roles share work with
          which Products), so you can study a slice of the method without the full
          activity detail.
        </p>
      </div>

      <div className="card section-gap">
        <h2 style={{ marginTop: 0 }}>Reading the codes</h2>
        <p>Edges are labelled with {fw.name}&rsquo;s cross-reference codes:</p>
        <ul className="bullets">
          {theme.codeGroups.map(({ group, codes }) => (
            <li key={group}>
              {codes.map((c, i) => (
                <span key={c.code}>
                  {i > 0 ? ' · ' : ''}
                  <strong>{c.code}</strong> {c.label}
                </span>
              ))}
              {' — for '}
              {andList(layersForGroup(group)).toLowerCase()}.
            </li>
          ))}
        </ul>
      </div>

      <div className="card">
        <h2 style={{ marginTop: 0 }}>A note on accuracy</h2>
        <p>{prose.accuracy}</p>
        {prose.related && <p className="muted">{prose.related}</p>}
      </div>
    </div>
  );
}
