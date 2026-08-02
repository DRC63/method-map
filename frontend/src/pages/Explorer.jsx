import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router';
import { api } from '../api/client';
import ControlPanel from '../components/ControlPanel';
import GraphCanvas from '../components/GraphCanvas';
import EntityDetailPanel from '../components/EntityDetailPanel';
import EntityForm from '../components/EntityForm';
import RelationshipForm from '../components/RelationshipForm';
import TimelineScrubber from '../components/TimelineScrubber';
import TimelineSwimlane from '../components/TimelineSwimlane';
import { makeFrameworkTheme } from '../theme/theme';
import { useAdmin } from '../context/AdminContext';

const STAGE_MS = 1600; // auto-play dwell per lifecycle stage

export default function Explorer() {
  const { isAdmin } = useAdmin();
  const [framework, setFramework] = useState(null);
  const [entities, setEntities] = useState([]);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [visibleTypes, setVisibleTypes] = useState(new Set());
  const [derived, setDerived] = useState(true);
  const [layout, setLayout] = useState('structured');
  const [search, setSearch] = useState('');
  const [controlsOpen, setControlsOpen] = useState(false); // mobile control-panel drawer
  const [selectedId, setSelectedId] = useState(null);
  const [loadingGraph, setLoadingGraph] = useState(true);
  const [dataToken, setDataToken] = useState(0);

  // timeline mode
  const [timelineIndex, setTimelineIndex] = useState(0);
  const [timelineMode, setTimelineMode] = useState('spotlight');
  const [playing, setPlaying] = useState(false);
  // The swimlane shows every stage at full strength until the scrubber is used;
  // once touched, the current stage is spotlit and the rest dim.
  const [timelineTouched, setTimelineTouched] = useState(false);

  // admin modals
  const [editingEntity, setEditingEntity] = useState(null);
  const [creatingEntity, setCreatingEntity] = useState(false);
  const [relPreset, setRelPreset] = useState(null); // {from} or {to}

  const graphRef = useRef(null);
  const [searchParams, setSearchParams] = useSearchParams();

  // Load the framework (a single-framework deployment names its default via
  // FRAMEWORK_KEY / /api/meta; otherwise use the first one).
  useEffect(() => {
    Promise.all([api.listFrameworks(), api.getMeta()]).then(([list, meta]) => {
      const def = meta.default_framework
        ? list.find((f) => f.key === meta.default_framework)
        : null;
      setFramework(def || list[0] || null);
    });
  }, []);

  const theme = useMemo(
    () => (framework ? makeFrameworkTheme(framework) : null),
    [framework],
  );

  // Default all layers on once the framework's type catalog is known.
  useEffect(() => {
    if (theme) setVisibleTypes(new Set(theme.types.map((t) => t.key)));
  }, [theme]);

  // Deep-link support: /?focus=<entityId> (e.g. from the Lifecycle view) selects
  // that node on arrival, then clears the param so it doesn't stick.
  useEffect(() => {
    const focus = searchParams.get('focus');
    if (focus) {
      setSelectedId(Number(focus));
      searchParams.delete('focus');
      setSearchParams(searchParams, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  const fkey = framework?.key;

  useEffect(() => {
    if (!fkey) return;
    api.listEntities(fkey).then(setEntities);
  }, [fkey, dataToken]);

  // (Re)load graph whenever the framework, visible layers or derived toggle change.
  useEffect(() => {
    if (!fkey || !theme || visibleTypes.size === 0) return;
    setLoadingGraph(true);
    const types = theme.types
      .map((t) => t.key)
      .filter((t) => visibleTypes.has(t))
      .join(',');
    api
      .getGraph(fkey, { types, derived })
      .then((g) => setGraphData({ nodes: g.nodes, links: g.links }))
      .finally(() => setLoadingGraph(false));
  }, [fkey, theme, visibleTypes, derived, dataToken]);

  const counts = framework?.entity_counts || {};
  const containerType = theme?.container ?? 'process';
  const hubType = theme?.hub ?? 'activity';
  const processes = useMemo(
    () => entities.filter((e) => e.type === containerType),
    [entities, containerType],
  );

  // ----- Timeline mode: one stage per container (process), in lifecycle
  // sequence. Each stage's highlight set = the container + its hubs (activities)
  // + every node those hubs connect to. -----
  const timelineStages = useMemo(() => {
    const nodes = graphData.nodes;
    if (!nodes.length) return [];
    const procs = nodes
      .filter((n) => n.type === containerType)
      .sort(
        (a, b) =>
          (a.sequence ?? a.sort_order ?? 0) - (b.sequence ?? b.sort_order ?? 0),
      );
    const actsByProc = new Map();
    nodes.forEach((n) => {
      if (n.type === hubType && n.parent_id != null) {
        if (!actsByProc.has(n.parent_id)) actsByProc.set(n.parent_id, []);
        actsByProc.get(n.parent_id).push(n.id);
      }
    });
    const nbr = new Map();
    graphData.links.forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (!nbr.has(s)) nbr.set(s, new Set());
      if (!nbr.has(t)) nbr.set(t, new Set());
      nbr.get(s).add(t);
      nbr.get(t).add(s);
    });
    return procs.map((p) => {
      const ids = new Set([p.id]);
      (actsByProc.get(p.id) || []).forEach((aid) => {
        ids.add(aid);
        (nbr.get(aid) || []).forEach((x) => ids.add(x));
      });
      return { process: p, ids };
    });
  }, [graphData, containerType, hubType]);

  const timelineSet = useMemo(() => {
    if (layout !== 'timeline' || !timelineStages.length || !timelineTouched) return null;
    const i = Math.min(timelineIndex, timelineStages.length - 1);
    if (timelineMode === 'cumulative') {
      const set = new Set();
      for (let k = 0; k <= i; k++) timelineStages[k].ids.forEach((x) => set.add(x));
      return set;
    }
    return timelineStages[i].ids;
  }, [layout, timelineStages, timelineIndex, timelineMode, timelineTouched]);

  // Reset the scrubber whenever timeline mode is (re)entered.
  useEffect(() => {
    if (layout === 'timeline') {
      setTimelineIndex(0);
      setPlaying(false);
      setTimelineTouched(false);
    } else {
      setPlaying(false);
    }
  }, [layout]);

  // Auto-play: advance one stage at a time, stopping at the end.
  useEffect(() => {
    if (!playing || layout !== 'timeline' || timelineStages.length === 0) return;
    const id = setInterval(() => {
      setTimelineIndex((i) => {
        if (i >= timelineStages.length - 1) {
          setPlaying(false);
          return i;
        }
        return i + 1;
      });
    }, STAGE_MS);
    return () => clearInterval(id);
  }, [playing, layout, timelineStages.length]);

  const toggleType = useCallback((type) => {
    setVisibleTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  }, []);

  const refreshData = useCallback(() => setDataToken((t) => t + 1), []);

  const exportPng = useCallback(() => {
    const url = graphRef.current?.exportPng();
    if (!url) return;
    // Stamp a "<Framework> Method Map" title band onto the exported graphic so
    // the image itself is clearly labelled (PRINCE2 vs MSP), not just its filename.
    const img = new Image();
    img.onload = () => {
      const scale = Math.max(1, img.width / 1200);
      const bandH = Math.round(56 * scale);
      const pad = Math.round(20 * scale);
      const c = document.createElement('canvas');
      c.width = img.width;
      c.height = img.height + bandH;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, c.width, c.height);
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#0B2545';
      ctx.font = `600 ${Math.round(24 * scale)}px system-ui, -apple-system, sans-serif`;
      ctx.fillText(`${framework.name} Method Map`, pad, bandH / 2);
      ctx.font = `700 ${Math.round(18 * scale)}px system-ui, -apple-system, sans-serif`;
      const wP3M = ctx.measureText('P3M').width;
      const wAI = ctx.measureText('AI').width;
      const brandX = c.width - pad - wP3M - wAI;
      ctx.fillStyle = '#0B2545'; // "P3M" navy
      ctx.fillText('P3M', brandX, bandH / 2);
      ctx.fillStyle = '#C9A227'; // "AI" gold
      ctx.fillText('AI', brandX + wP3M, bandH / 2);
      ctx.fillStyle = '#E3E8EF';
      ctx.fillRect(0, bandH - Math.max(1, Math.round(scale)), c.width, Math.max(1, Math.round(scale)));
      ctx.drawImage(img, 0, bandH);
      const a = document.createElement('a');
      a.href = c.toDataURL('image/png');
      a.download = `${fkey || 'method-map'}-graph.png`;
      a.click();
    };
    img.src = url;
  }, [fkey, framework]);

  if (!framework) {
    return <div className="graph-empty">Loading framework…</div>;
  }

  return (
    <div className={`explorer ${controlsOpen ? 'controls-open' : ''}`}>
      <button
        className="mobile-controls-toggle"
        onClick={() => setControlsOpen((o) => !o)}
        aria-label="Toggle controls"
      >
        {controlsOpen ? '✕ Close' : '☰ Controls'}
      </button>
      {controlsOpen && (
        <div className="mobile-drawer-backdrop" onClick={() => setControlsOpen(false)} />
      )}
      <ControlPanel
        frameworkKey={fkey}
        theme={theme}
        counts={counts}
        visibleTypes={visibleTypes}
        onToggleType={toggleType}
        derived={derived}
        onToggleDerived={() => setDerived((d) => !d)}
        layout={layout}
        onSetLayout={setLayout}
        search={search}
        onSearch={setSearch}
        onExportPng={exportPng}
      />

      <div className={`graph-stage ${layout === 'timeline' ? 'is-timeline' : ''}`}>
        {graphData.nodes.length === 0 && !loadingGraph && layout !== 'timeline' && (
          <div className="graph-empty">No entities in the selected layers.</div>
        )}
        {layout === 'timeline' ? (
          <TimelineSwimlane
            data={graphData}
            theme={theme}
            selectedId={selectedId}
            onSelectNode={setSelectedId}
            timelineSet={timelineSet}
          />
        ) : (
          <>
            <GraphCanvas
              ref={graphRef}
              data={graphData}
              selectedId={selectedId}
              onSelectNode={setSelectedId}
              search={search}
              layout={layout}
              timelineSet={timelineSet}
              theme={theme}
            />
            <div className="graph-hint">
              {graphData.nodes.length} nodes · {graphData.links.length} links · drag to
              pan, scroll to zoom, click a node for detail
            </div>
          </>
        )}
        {layout === 'timeline' && (
          <TimelineScrubber
            stages={timelineStages}
            index={timelineIndex}
            onIndex={(i) => {
              setPlaying(false);
              setTimelineTouched(true);
              setTimelineIndex(i);
            }}
            playing={playing}
            onTogglePlay={() => {
              setTimelineTouched(true);
              setPlaying((p) => !p);
            }}
            mode={timelineMode}
            onSetMode={(m) => {
              setTimelineTouched(true);
              setTimelineMode(m);
            }}
          />
        )}
        {isAdmin && (
          <button
            className="btn btn-accent btn-sm"
            style={{ position: 'absolute', top: 14, right: 14 }}
            onClick={() => setCreatingEntity(true)}
          >
            + Add entity
          </button>
        )}
      </div>

      {selectedId != null && (
        <EntityDetailPanel
          frameworkKey={fkey}
          theme={theme}
          entityId={selectedId}
          reloadToken={dataToken}
          onSelect={setSelectedId}
          onClose={() => setSelectedId(null)}
          onEdit={(ent) => setEditingEntity(ent)}
          onAddRelationship={(ent) =>
            setRelPreset(ent.type === 'activity' ? { from: ent.id } : { to: ent.id })
          }
          onChanged={refreshData}
        />
      )}

      {(editingEntity || creatingEntity) && (
        <EntityForm
          frameworkId={framework.id}
          entity={editingEntity}
          processes={processes}
          onClose={() => {
            setEditingEntity(null);
            setCreatingEntity(false);
          }}
          onSaved={() => {
            setEditingEntity(null);
            setCreatingEntity(false);
            refreshData();
          }}
        />
      )}

      {relPreset && (
        <RelationshipForm
          frameworkId={framework.id}
          entities={entities}
          presetFrom={relPreset.from}
          presetTo={relPreset.to}
          onClose={() => setRelPreset(null)}
          onSaved={() => {
            setRelPreset(null);
            refreshData();
          }}
        />
      )}
    </div>
  );
}
