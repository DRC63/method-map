import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router';
import { api } from '../api/client';
import ControlPanel from '../components/ControlPanel';
import GraphCanvas from '../components/GraphCanvas';
import EntityDetailPanel from '../components/EntityDetailPanel';
import EntityForm from '../components/EntityForm';
import RelationshipForm from '../components/RelationshipForm';
import { useAdmin } from '../context/AdminContext';

const ALL_TYPES = ['process', 'activity', 'role', 'practice', 'approach', 'product'];

export default function Explorer() {
  const { isAdmin } = useAdmin();
  const [framework, setFramework] = useState(null);
  const [entities, setEntities] = useState([]);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [visibleTypes, setVisibleTypes] = useState(new Set(ALL_TYPES));
  const [derived, setDerived] = useState(true);
  const [layout, setLayout] = useState('structured');
  const [search, setSearch] = useState('');
  const [selectedId, setSelectedId] = useState(null);
  const [loadingGraph, setLoadingGraph] = useState(true);
  const [dataToken, setDataToken] = useState(0);

  // admin modals
  const [editingEntity, setEditingEntity] = useState(null);
  const [creatingEntity, setCreatingEntity] = useState(false);
  const [relPreset, setRelPreset] = useState(null); // {from} or {to}

  const graphRef = useRef(null);
  const [searchParams, setSearchParams] = useSearchParams();

  // Load framework + entities once (and after admin edits via dataToken).
  useEffect(() => {
    api.listFrameworks().then((list) => setFramework(list[0] || null));
  }, []);

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
    if (!fkey) return;
    setLoadingGraph(true);
    const types = ALL_TYPES.filter((t) => visibleTypes.has(t)).join(',');
    api
      .getGraph(fkey, { types, derived })
      .then((g) => setGraphData({ nodes: g.nodes, links: g.links }))
      .finally(() => setLoadingGraph(false));
  }, [fkey, visibleTypes, derived, dataToken]);

  const counts = framework?.entity_counts || {};
  const processes = useMemo(
    () => entities.filter((e) => e.type === 'process'),
    [entities],
  );

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
    const a = document.createElement('a');
    a.href = url;
    a.download = `${fkey || 'method-map'}-graph.png`;
    a.click();
  }, [fkey]);

  if (!framework) {
    return <div className="graph-empty">Loading framework…</div>;
  }

  return (
    <div className="explorer">
      <ControlPanel
        frameworkKey={fkey}
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

      <div className="graph-stage">
        {graphData.nodes.length === 0 && !loadingGraph && (
          <div className="graph-empty">No entities in the selected layers.</div>
        )}
        <GraphCanvas
          ref={graphRef}
          data={graphData}
          selectedId={selectedId}
          onSelectNode={setSelectedId}
          search={search}
          layout={layout}
        />
        <div className="graph-hint">
          {graphData.nodes.length} nodes · {graphData.links.length} links · drag to
          pan, scroll to zoom, click a node for detail
        </div>
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
