import { entityColors } from '../theme/theme';

// Control bar for the Timeline view. Left to right: play/pause (auto-advances
// through the lifecycle stages), a slider + labelled stage ticks to scrub to any
// stage, a Spotlight/Cumulative toggle (show one stage, or everything up to it),
// and a Reset button. It holds no state of its own — every control calls back up
// to Explorer, which owns the stage index, mode and selection. `onReset` is
// optional; the button only renders when the parent provides it.
export default function TimelineScrubber({
  stages,
  index,
  onIndex,
  playing,
  onTogglePlay,
  mode,
  onSetMode,
  onReset,
}) {
  if (!stages.length) return null;
  const current = stages[Math.min(index, stages.length - 1)];
  const p = current.process;

  return (
    <div className="timeline-bar">
      <button
        className="timeline-play"
        onClick={onTogglePlay}
        aria-label={playing ? 'Pause' : 'Play'}
        title={playing ? 'Pause' : 'Play through the lifecycle'}
      >
        {playing ? '❚❚' : '▶'}
      </button>

      <div className="timeline-slider-wrap">
        <div className="timeline-stage-label">
          <span className="timeline-step" style={{ background: entityColors.process }}>
            {p.code}
          </span>
          <strong>{p.name}</strong>
          <span className="timeline-count">
            stage {index + 1} / {stages.length}
          </span>
        </div>
        <input
          className="timeline-range"
          type="range"
          min={0}
          max={stages.length - 1}
          step={1}
          value={index}
          onChange={(e) => onIndex(Number(e.target.value))}
        />
        <div className="timeline-ticks">
          {stages.map((s, i) => (
            <button
              key={s.process.id}
              className={`timeline-tick ${i === index ? 'active' : ''} ${i < index ? 'past' : ''}`}
              onClick={() => onIndex(i)}
              title={s.process.name}
            >
              {s.process.code}
            </button>
          ))}
        </div>
      </div>

      <div className="timeline-mode">
        <button
          className={`timeline-mode-opt ${mode === 'spotlight' ? 'active' : ''}`}
          onClick={() => onSetMode('spotlight')}
          title="Highlight only the current stage"
        >
          Spotlight
        </button>
        <button
          className={`timeline-mode-opt ${mode === 'cumulative' ? 'active' : ''}`}
          onClick={() => onSetMode('cumulative')}
          title="Highlight everything up to the current stage"
        >
          Cumulative
        </button>
      </div>

      {onReset && (
        <button
          className="timeline-reset"
          onClick={onReset}
          title="Clear the selection and reset the timeline to the full view"
        >
          Reset
        </button>
      )}
    </div>
  );
}
