import { useCallback, useEffect, useImperativeHandle, useLayoutEffect, useMemo, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { codeColors, entityColors, linkKindColors } from '../theme/theme';
import { computeStructuredLayout } from '../theme/graphLayout';

// Renders the node/link graph. Handles sizing, neighbour highlighting on
// hover/selection, per-type node colouring, and code-coloured edges. In
// 'structured' layout the nodes are pinned into a fixed matrix (processes top,
// activities below, products under them, roles left, practices right, approaches
// bottom); in 'force' layout they float freely. Exposes `exportPng()` and
// `zoomToFit()` to the parent via ref.
export default function GraphCanvas({ ref, data, selectedId, onSelectNode, search, layout = 'structured' }) {
  const wrapRef = useRef(null);
  const fgRef = useRef(null);
  const zonesRef = useRef([]);
  const [size, setSize] = useState({ width: 800, height: 600 });
  const [hoverId, setHoverId] = useState(null);

  // Measure container. useLayoutEffect + a synchronous getBoundingClientRect so
  // the canvas gets real dimensions on first paint even if the ResizeObserver's
  // initial delivery is delayed; RO + window resize keep it in sync afterwards.
  useLayoutEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const measure = () => {
      const rect = el.getBoundingClientRect();
      if (rect.width && rect.height) {
        setSize({ width: rect.width, height: rect.height });
      }
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    window.addEventListener('resize', measure);
    return () => {
      ro.disconnect();
      window.removeEventListener('resize', measure);
    };
  }, []);

  // Apply / clear the fixed matrix layout. In structured mode every node gets
  // fx/fy so d3-force pins it; in force mode we strip them so the simulation
  // takes over. We mutate the very node objects the graph holds (not clones) to
  // avoid link source/target aliasing, then reheat and refit.
  useEffect(() => {
    if (!data.nodes.length) return;
    if (layout === 'structured') {
      const { pos, zones } = computeStructuredLayout(data.nodes);
      zonesRef.current = zones;
      data.nodes.forEach((n) => {
        const p = pos.get(n.id);
        if (p) {
          n.fx = p.x;
          n.fy = p.y;
          n.x = p.x;
          n.y = p.y;
        }
      });
    } else {
      zonesRef.current = [];
      data.nodes.forEach((n) => {
        delete n.fx;
        delete n.fy;
      });
    }
    fgRef.current?.d3ReheatSimulation?.();
    const t = setTimeout(() => fgRef.current?.zoomToFit(500, 70), 120);
    return () => clearTimeout(t);
  }, [data, layout]);

  // Draw the horizontal, colour-coded zone labels behind the nodes (structured
  // layout only). Large, bold and tinted to each region's entity colour.
  const paintZones = useCallback((ctx, globalScale) => {
    const zones = zonesRef.current;
    if (!zones.length) return;
    const fontSize = Math.max(26 / globalScale, 13);
    ctx.save();
    ctx.font = `800 ${fontSize}px Poppins, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.globalAlpha = 0.9;
    zones.forEach((z) => {
      ctx.fillStyle = z.color || 'rgba(11, 37, 69, 0.6)';
      ctx.fillText(z.label, z.x, z.y);
    });
    ctx.globalAlpha = 1;
    ctx.restore();
  }, []);

  // Adjacency for neighbour highlighting.
  const adjacency = useMemo(() => {
    const map = new Map();
    data.links.forEach((l) => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      if (!map.has(s)) map.set(s, new Set());
      if (!map.has(t)) map.set(t, new Set());
      map.get(s).add(t);
      map.get(t).add(s);
    });
    return map;
  }, [data]);

  const searchLower = (search || '').trim().toLowerCase();
  const searchMatches = useMemo(() => {
    if (!searchLower) return null;
    return new Set(
      data.nodes.filter((n) => n.name.toLowerCase().includes(searchLower)).map((n) => n.id),
    );
  }, [data, searchLower]);

  const focusId = hoverId ?? selectedId;
  const highlightSet = useMemo(() => {
    if (focusId == null) return null;
    const set = new Set([focusId]);
    (adjacency.get(focusId) || new Set()).forEach((id) => set.add(id));
    return set;
  }, [focusId, adjacency]);

  useImperativeHandle(ref, () => ({
    zoomToFit: () => fgRef.current?.zoomToFit(500, 60),
    exportPng: () => {
      const canvas = wrapRef.current?.querySelector('canvas');
      if (!canvas) return null;
      return canvas.toDataURL('image/png');
    },
  }));

  // Node size weighting. The matrix layout sizes by DIRECT responsibilities —
  // the count of real C/P/N/I/O/U/A relationships the node takes part in (for
  // processes: how many activities they contain), independent of the visible
  // layers and the indirect-links toggle. Full-range sqrt scale (area ∝ count)
  // sized up to read at the zoomed-out matrix scale. The force layout keeps its
  // original degree-based capped scaling.
  const nodeVal = useCallback(
    (n) => {
      if (layout === 'structured') return 6.5 + Math.sqrt(n.direct_degree || 0) * 3.3;
      return 3 + Math.min(n.degree || 0, 12) * 0.8;
    },
    [layout],
  );

  const paintNode = useCallback(
    (node, ctx, globalScale) => {
      const r = nodeVal(node);
      const dimmed = highlightSet && !highlightSet.has(node.id);
      const isSearchHit = searchMatches && searchMatches.has(node.id);
      const isSelected = node.id === selectedId;

      ctx.globalAlpha = dimmed ? 0.15 : 1;
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
      ctx.fillStyle = entityColors[node.type] || '#888';
      ctx.fill();

      if (isSelected || isSearchHit) {
        ctx.lineWidth = 2 / globalScale;
        ctx.strokeStyle = isSelected ? '#0B2545' : '#C9A227';
        ctx.stroke();
      }
      // indicative entities get a subtle dashed ring
      if (node.confidence === 'indicative' && !dimmed) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, r + 1.6 / globalScale, 0, 2 * Math.PI);
        ctx.setLineDash([1.5 / globalScale, 1.5 / globalScale]);
        ctx.lineWidth = 0.8 / globalScale;
        ctx.strokeStyle = 'rgba(168,132,28,0.9)';
        ctx.stroke();
        ctx.setLineDash([]);
      }

      // In the structured matrix the "axis" nodes (everything but activities)
      // are always labelled so the regions read clearly; activities label on
      // zoom/hover/select to avoid clutter.
      const alwaysLabel = layout === 'structured' && node.type !== 'activity';
      const showLabel =
        alwaysLabel ||
        globalScale > 1.6 ||
        isSelected ||
        (highlightSet && highlightSet.has(node.id)) ||
        isSearchHit;
      if (showLabel) {
        const label = node.code ? `${node.code} · ${node.name}` : node.name;
        const fontSize = Math.max(10 / globalScale, 2.2);
        ctx.font = `${fontSize}px Poppins, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillStyle = dimmed ? 'rgba(28,43,58,0.3)' : '#1C2B3A';
        ctx.fillText(label, node.x, node.y + r + 1);
      }
      ctx.globalAlpha = 1;
    },
    [highlightSet, searchMatches, selectedId, nodeVal, layout],
  );

  const paintPointerArea = useCallback(
    (node, color, ctx) => {
      ctx.fillStyle = color;
      const r = nodeVal(node) + 2;
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
      ctx.fill();
    },
    [nodeVal],
  );

  const linkColor = useCallback(
    (link) => {
      const s = typeof link.source === 'object' ? link.source.id : link.source;
      const t = typeof link.target === 'object' ? link.target.id : link.target;
      const dimmed = highlightSet && !(highlightSet.has(s) && highlightSet.has(t));
      let base;
      if (link.kind === 'direct') base = codeColors[link.code] || '#7a8290';
      else base = linkKindColors[link.kind] || 'rgba(120,130,145,0.3)';
      if (dimmed) return 'rgba(120,130,145,0.06)';
      return base;
    },
    [highlightSet],
  );

  const linkWidth = useCallback(
    (link) => {
      const s = typeof link.source === 'object' ? link.source.id : link.source;
      const t = typeof link.target === 'object' ? link.target.id : link.target;
      const active = highlightSet && highlightSet.has(s) && highlightSet.has(t);
      if (link.kind === 'derived') return active ? 1.4 : 0.5 + Math.min(link.weight, 5) * 0.15;
      return active ? 2.4 : 1;
    },
    [highlightSet],
  );

  return (
    <div ref={wrapRef} style={{ position: 'absolute', inset: 0 }}>
      <ForceGraph2D
        ref={fgRef}
        width={size.width}
        height={size.height}
        graphData={data}
        backgroundColor="rgba(0,0,0,0)"
        nodeRelSize={1}
        nodeVal={nodeVal}
        nodeCanvasObject={paintNode}
        nodePointerAreaPaint={paintPointerArea}
        linkColor={linkColor}
        linkWidth={linkWidth}
        linkDirectionalArrowLength={(l) => (l.kind === 'direct' ? 2.5 : 0)}
        linkDirectionalArrowRelPos={1}
        cooldownTicks={layout === 'structured' ? 0 : 120}
        onRenderFramePre={paintZones}
        onNodeHover={(n) => setHoverId(n ? n.id : null)}
        onNodeClick={(n) => onSelectNode(n ? n.id : null)}
        onBackgroundClick={() => onSelectNode(null)}
        onEngineStop={() => fgRef.current?.zoomToFit(400, 60)}
      />
    </div>
  );
}
