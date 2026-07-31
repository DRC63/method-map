import { entityColors, entityTypeLabels } from '../theme/theme';

const TYPES = ['process', 'activity', 'role', 'practice', 'approach', 'product'];

export default function Guide() {
  return (
    <div className="prose">
      <div className="card section-gap">
        <h2 style={{ marginTop: 0 }}>What this is</h2>
        <p>
          The Method Map turns PRINCE2 7 into an interactive network. Every
          management <strong>activity</strong> is cross-referenced to the roles that
          perform it, the practices and management approaches it draws on, and the
          management products it takes in or creates. Explore how any one element
          connects to the rest of the method — useful when tailoring a project,
          onboarding a team, or explaining governance to a client.
        </p>
      </div>

      <div className="card section-gap">
        <h2 style={{ marginTop: 0 }}>Two ways to look at it</h2>
        <ul className="bullets">
          <li><strong>Method Explorer</strong> — the interdependency network. Best for "what connects to what": pick any element and trace its links across the whole method.</li>
          <li><strong>Project Lifecycle</strong> — the same processes laid out in time. The classic PRINCE2 process model: time runs left→right (Pre-project → Initiation → Delivery stages ⟳ → Final stage) across three swimlanes (Directing / Managing / Delivering). Click a process to see its activities in sequence.</li>
        </ul>
      </div>

      <div className="card section-gap">
        <h2 style={{ marginTop: 0 }}>The six layers</h2>
        <div style={{ display: 'grid', gap: 8 }}>
          {TYPES.map((t) => (
            <div key={t} className="legend-item" style={{ fontSize: '0.95rem' }}>
              <span className="layer-swatch" style={{ background: entityColors[t] }} />
              <strong style={{ textTransform: 'capitalize', color: 'var(--color-text)' }}>
                {entityTypeLabels[t]}
              </strong>
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
        <p>Edges are labelled with the standard PRINCE2 cross-reference codes:</p>
        <ul className="bullets">
          <li><strong>C</strong> Responsible · <strong>P</strong> Participates · <strong>N</strong> Assists — for roles, practices and management approaches.</li>
          <li><strong>I</strong> Input · <strong>O</strong> Output · <strong>U</strong> Update · <strong>A</strong> Authorise — for management products.</li>
        </ul>
      </div>

      <div className="card">
        <h2 style={{ marginTop: 0 }}>A note on accuracy</h2>
        <p>
          Process, role, practice, approach and product <em>names</em> are corroborated
          across public sources. The activity-level breakdown and its codes are a
          best-effort reconstruction (from prince2.wiki, CC-BY 4.0) and are shown with a
          dashed <span className="confidence-flag confidence-indicative">◌ indicative</span>{' '}
          marker. Verify against the licensed PRINCE2 manual before using any of this as
          formal audit, training or certification evidence.
        </p>
        <p className="muted">
          MSP 5th Edition is on the roadmap — the app is built to hold multiple
          frameworks, so it slots in alongside PRINCE2 without a rebuild.
        </p>
      </div>
    </div>
  );
}
