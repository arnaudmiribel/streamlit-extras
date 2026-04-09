import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import Graph from "graphology";
import FA2Layout from "graphology-layout-forceatlas2/worker";
import { FC, ReactElement, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Sigma from "sigma";
import { Settings } from "sigma/settings";
import { NodeDisplayData, EdgeDisplayData } from "sigma/types";

export type SigmaGraphStateShape = {
  selection: {
    type: "node" | "edge";
    id: string;
    attributes: Record<string, unknown>;
  } | null;
};

type GraphNode = {
  id: string;
  label?: string;
  x?: number;
  y?: number;
  size?: number;
  color?: string;
  hidden?: boolean;
  forceLabel?: boolean;
  zIndex?: number;
  [key: string]: unknown;
};

type GraphEdge = {
  source: string;
  target: string;
  key?: string;
  label?: string;
  size?: number;
  color?: string;
  hidden?: boolean;
  zIndex?: number;
  [key: string]: unknown;
};

type GraphData = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  directed: boolean;
  multigraph: boolean;
};

type SelectionState = {
  type: "node" | "edge";
  id: string;
} | null;

type NodeSizeConfig =
  | { mode: "uniform"; value: number }
  | { mode: "degree" }
  | { mode: "attribute"; attribute: string };

export type SigmaGraphDataShape = {
  graph: GraphData;
  useForceLayout: boolean;
  width: "stretch" | number;
  height: number;
  nodeColor: string | null;
  edgeColor: string | null;
  nodeSizeConfig: NodeSizeConfig;
  selectionMode: "nodes" | "edges" | "all";
  selectionEnabled: boolean;
  currentSelection: SelectionState;
};

export type SigmaGraphProps = Pick<
  FrontendRendererArgs<SigmaGraphStateShape, SigmaGraphDataShape>,
  "setStateValue"
> & {
  graph: GraphData;
  useForceLayout: boolean;
  width: "stretch" | number;
  height: number;
  nodeColor: string | null;
  edgeColor: string | null;
  nodeSizeConfig: NodeSizeConfig;
  selectionMode: "nodes" | "edges" | "all";
  selectionEnabled: boolean;
  currentSelection: SelectionState;
};

// Parse a color string to RGB values (used for blending)
function parseColor(color: string): [number, number, number] | null {
  // Handle hex colors
  if (color.startsWith("#")) {
    let hex = color.slice(1);
    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    if (hex.length === 8) {
      hex = hex.slice(0, 6);
    }
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return [r, g, b];
  }

  // Handle rgb/rgba
  const rgbMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (rgbMatch) {
    return [parseInt(rgbMatch[1]), parseInt(rgbMatch[2]), parseInt(rgbMatch[3])];
  }

  return null;
}

// Blend a color with the background color (0 = full background, 1 = full color)
function blendWithBackground(color: string, backgroundColor: string, amount: number): string {
  const fg = parseColor(color);
  const bg = parseColor(backgroundColor);

  if (!fg || !bg) return color;

  const r = Math.round(bg[0] + (fg[0] - bg[0]) * amount);
  const g = Math.round(bg[1] + (fg[1] - bg[1]) * amount);
  const b = Math.round(bg[2] + (fg[2] - bg[2]) * amount);

  return `rgb(${r}, ${g}, ${b})`;
}

// Create a custom hover drawing function with themed label background
function createThemedHoverDrawer(labelBackgroundColor: string, labelTextColor: string) {
  return (
    context: CanvasRenderingContext2D,
    data: { x: number; y: number; size: number; label?: string | null; color: string },
    settings: Settings,
  ) => {
    // Draw halo (larger circle behind the node)
    const size = data.size;
    context.beginPath();
    context.arc(data.x, data.y, size + 4, 0, Math.PI * 2);
    context.closePath();
    context.fillStyle = data.color;
    context.globalAlpha = 0.3;
    context.fill();
    context.globalAlpha = 1;

    // Draw label with background if label exists
    if (data.label) {
      const font = `${settings.labelWeight} ${settings.labelSize}px ${settings.labelFont}`;
      context.font = font;

      const labelWidth = context.measureText(data.label).width;
      const labelHeight = settings.labelSize;
      const padding = 2;
      const radius = 2;

      const labelX = data.x + size + 6;
      const labelY = data.y + labelHeight / 3;

      // Draw rounded rectangle background
      const rectX = labelX - padding;
      const rectY = data.y - labelHeight / 2 - padding;
      const rectW = labelWidth + padding * 2;
      const rectH = labelHeight + padding * 2;

      context.beginPath();
      context.roundRect(rectX, rectY, rectW, rectH, radius);
      context.fillStyle = labelBackgroundColor;
      context.fill();

      // Draw label text
      context.fillStyle = labelTextColor;
      context.fillText(data.label, labelX, labelY);
    }
  };
}

/**
 * A network graph visualization component using sigma.js.
 */
const SigmaGraph: FC<SigmaGraphProps> = ({
  graph: graphData,
  useForceLayout,
  width,
  height,
  nodeColor,
  edgeColor,
  nodeSizeConfig,
  selectionMode,
  selectionEnabled,
  currentSelection,
  setStateValue,
}): ReactElement => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sigmaRef = useRef<Sigma | null>(null);
  const graphRef = useRef<Graph | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Fallback colors (used when CSS variables aren't available)
  const fallbackColors = {
    primaryColor: "#ff4b4b",
    textColor: "#262730",
    backgroundColor: "#ffffff",
    secondaryBackgroundColor: "#f0f2f6",
    borderColor: "#d3d3d3",
  };

  // Read theme colors from Streamlit's CSS variables
  const [themeColors, setThemeColors] = useState(fallbackColors);
  const lastThemeHash = useRef<string>("");

  useEffect(() => {
    if (!containerRef.current) return;

    // Get the host element (shadow root host) or fall back to container
    const root = containerRef.current.getRootNode() as ShadowRoot;
    const host = root?.host ?? containerRef.current;

    // Helper to read a CSS variable with fallback
    const getCssVar = (name: string, fallback: string): string => {
      const value = getComputedStyle(host).getPropertyValue(name).trim();
      return value || fallback;
    };

    // Function to read all theme colors from CSS variables
    const updateThemeFromCssVars = () => {
      const colors = {
        primaryColor: getCssVar("--st-primary-color", fallbackColors.primaryColor),
        textColor: getCssVar("--st-text-color", fallbackColors.textColor),
        backgroundColor: getCssVar("--st-background-color", fallbackColors.backgroundColor),
        secondaryBackgroundColor: getCssVar("--st-secondary-background-color", fallbackColors.secondaryBackgroundColor),
        borderColor: getCssVar("--st-border-color", fallbackColors.borderColor),
      };

      // Only update if colors actually changed (avoid unnecessary re-renders)
      const hash = JSON.stringify(colors);
      if (hash !== lastThemeHash.current) {
        lastThemeHash.current = hash;
        setThemeColors(colors);
      }
    };

    // Initial detection
    updateThemeFromCssVars();

    // Poll for CSS variable changes since MutationObserver doesn't catch
    // inherited/cascading CSS custom property changes
    const intervalId = setInterval(updateThemeFromCssVars, 100);

    return () => clearInterval(intervalId);
  }, []);

  // Refs to store latest handler functions (avoids recreating sigma on selection change)
  const handleNodeClickRef = useRef<(nodeId: string) => void>(() => {});
  const handleEdgeClickRef = useRef<(edgeKey: string) => void>(() => {});

  // Compute default colors from theme
  const defaultNodeColor = nodeColor || themeColors.primaryColor;
  // Use a muted version of textColor for edges (better contrast in both modes)
  const defaultEdgeColor = edgeColor || blendWithBackground(themeColors.textColor, themeColors.backgroundColor, 0.4);

  // Memoize nodeSizeConfig to avoid unnecessary re-renders
  // (the object reference changes on each render from Python even with same values)
  const stableNodeSizeConfig = useMemo(
    () => nodeSizeConfig,
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(nodeSizeConfig)],
  );

  // Memoize graphData to avoid unnecessary re-renders
  const stableGraphData = useMemo(
    () => graphData,
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(graphData)],
  );

  // Handle node click
  const handleNodeClick = useCallback(
    (nodeId: string) => {
      if (!selectionEnabled) return;
      if (selectionMode === "edges") return;

      const graph = graphRef.current;
      if (!graph) return;

      const attributes = graph.getNodeAttributes(nodeId);
      setStateValue("selection", {
        type: "node",
        id: nodeId,
        attributes,
      });
    },
    [selectionEnabled, selectionMode, setStateValue],
  );

  // Handle edge click
  const handleEdgeClick = useCallback(
    (edgeKey: string) => {
      if (!selectionEnabled) return;
      if (selectionMode === "nodes") return;

      const graph = graphRef.current;
      if (!graph) return;

      const attributes = graph.getEdgeAttributes(edgeKey);
      setStateValue("selection", {
        type: "edge",
        id: edgeKey,
        attributes,
      });
    },
    [selectionEnabled, selectionMode, setStateValue],
  );

  // Keep refs updated with latest handlers
  useEffect(() => {
    handleNodeClickRef.current = handleNodeClick;
    handleEdgeClickRef.current = handleEdgeClick;
  }, [handleNodeClick, handleEdgeClick]);

  // Initialize sigma and graph
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Create graphology graph
    const graph = new Graph({
      type: stableGraphData.directed ? "directed" : "undirected",
      multi: stableGraphData.multigraph,
    });

    // Helper to calculate node size based on config
    const getNodeSize = (node: GraphNode, degree?: number): number => {
      switch (stableNodeSizeConfig.mode) {
        case "uniform":
          return stableNodeSizeConfig.value;
        case "degree":
          // Degree-based sizing will be applied after edges are added
          // For now, return a placeholder
          return degree !== undefined ? 4 + degree * 1.5 : 8;
        case "attribute": {
          const value = node[stableNodeSizeConfig.attribute];
          return typeof value === "number" ? value : 8;
        }
      }
    };

    // Add nodes (with temporary size for degree mode)
    for (const node of stableGraphData.nodes) {
      const { id, ...attrs } = node;
      const hasExplicitColor = !!attrs.color;
      const nodeAttrs: Record<string, unknown> = {
        label: attrs.label ?? String(id),
        x: attrs.x ?? Math.random() * 100,
        y: attrs.y ?? Math.random() * 100,
        size: getNodeSize(node),
        color: attrs.color || defaultNodeColor,
        hidden: attrs.hidden ?? false,
        forceLabel: attrs.forceLabel ?? false,
        _hasExplicitColor: hasExplicitColor,
        ...attrs,
      };
      graph.addNode(id, nodeAttrs);
    }

    // Add edges
    for (const edge of stableGraphData.edges) {
      const { source, target, key, ...attrs } = edge;
      const edgeKey = key ?? `${source}-${target}`;
      const hasExplicitColor = !!attrs.color;
      const edgeAttrs: Record<string, unknown> = {
        label: attrs.label,
        size: attrs.size ?? 1,
        color: attrs.color || defaultEdgeColor,
        hidden: attrs.hidden ?? false,
        _hasExplicitColor: hasExplicitColor,
        ...attrs,
      };
      try {
        graph.addEdgeWithKey(edgeKey, source, target, edgeAttrs);
      } catch {
        // Edge might already exist in non-multigraph mode
        if (!stableGraphData.multigraph) {
          // Update existing edge
          const existingKey = graph.edge(source, target);
          if (existingKey) {
            graph.mergeEdgeAttributes(existingKey, edgeAttrs);
          }
        }
      }
    }

    // Apply degree-based sizing now that all edges are added
    if (stableNodeSizeConfig.mode === "degree") {
      graph.forEachNode((nodeId) => {
        const degree = graph.degree(nodeId);
        graph.setNodeAttribute(nodeId, "size", 4 + degree * 1.5);
      });
    }

    graphRef.current = graph;

    // Sigma settings - use theme colors
    const settings: Partial<Settings> = {
      defaultNodeColor,
      defaultEdgeColor,
      renderEdgeLabels: false,
      labelRenderedSizeThreshold: 8,
      labelDensity: 0.1,
      labelGridCellSize: 60,
      labelFont: "var(--st-font, sans-serif)",
      labelSize: 12,
      labelWeight: "500",
      labelColor: { color: themeColors.textColor },
      edgeLabelFont: "var(--st-font, sans-serif)",
      edgeLabelSize: 10,
      // Custom hover drawer with themed label background
      defaultDrawNodeHover: createThemedHoverDrawer(
        themeColors.secondaryBackgroundColor,
        themeColors.textColor,
      ),
      // Enable z-index based rendering for proper layering on hover
      zIndex: true,
      // Enable edge events only when selection mode includes edges
      enableEdgeEvents: selectionMode === "edges" || selectionMode === "all",
    };

    // Create sigma instance first so we can see the animation
    const sigma = new Sigma(graph, container, settings);
    sigmaRef.current = sigma;

    // Start animated ForceAtlas2 layout if requested
    let fa2Layout: FA2Layout | null = null;
    if (useForceLayout) {
      const nodeCount = graph.order;

      fa2Layout = new FA2Layout(graph, {
        settings: {
          // Very low gravity to allow nodes to spread out significantly
          gravity: nodeCount > 500 ? 0.001 : nodeCount > 100 ? 0.005 : 0.02,
          // Very high scaling ratio = strong repulsion between nodes
          scalingRatio: nodeCount > 500 ? 500 : nodeCount > 100 ? 200 : 50,
          // Strong gravity pulls disconnected components toward center
          strongGravityMode: false,
          // Barnes-Hut optimization for large graphs
          barnesHutOptimize: nodeCount > 50,
          barnesHutTheta: 0.5,
          // Slower convergence = more stable result
          slowDown: 1 + Math.log10(nodeCount + 1),
          // Edge weight influence
          edgeWeightInfluence: 1,
        },
      });

      // Start the layout animation
      fa2Layout.start();

      // Auto-stop after some time based on graph size
      const duration = Math.min(15000, Math.max(3000, nodeCount * 10));
      setTimeout(() => {
        if (fa2Layout && fa2Layout.isRunning()) {
          fa2Layout.stop();
        }
      }, duration);
    }

    // Set up event handlers
    sigma.on("enterNode", ({ node }) => {
      setHoveredNode(node);
    });

    sigma.on("leaveNode", () => {
      setHoveredNode(null);
    });

    sigma.on("clickNode", ({ node }) => {
      handleNodeClickRef.current(node);
    });

    sigma.on("clickEdge", ({ edge }) => {
      handleEdgeClickRef.current(edge);
    });

    // Cleanup
    return () => {
      if (fa2Layout) {
        fa2Layout.kill();
      }
      sigma.kill();
      sigmaRef.current = null;
      graphRef.current = null;
    };
  }, [
    stableGraphData,
    useForceLayout,
    stableNodeSizeConfig,
    selectionMode,
    defaultNodeColor,
    defaultEdgeColor,
  ]);

  // Update sigma settings when theme changes (without recreating the graph)
  useEffect(() => {
    const sigma = sigmaRef.current;
    const graph = graphRef.current;
    if (!sigma || !graph) return;

    // Update sigma settings
    sigma.setSetting("defaultNodeColor", defaultNodeColor);
    sigma.setSetting("defaultEdgeColor", defaultEdgeColor);
    sigma.setSetting("labelColor", { color: themeColors.textColor });
    sigma.setSetting(
      "defaultDrawNodeHover",
      createThemedHoverDrawer(themeColors.secondaryBackgroundColor, themeColors.textColor)
    );

    // Force update by touching graph attributes - this triggers graphology events
    // which sigma listens to for automatic re-renders
    graph.forEachNode((nodeId, attrs) => {
      // Only update nodes that don't have explicit colors
      if (!attrs._hasExplicitColor) {
        graph.setNodeAttribute(nodeId, "color", defaultNodeColor);
      }
    });

    graph.forEachEdge((edgeKey, attrs) => {
      // Only update edges that don't have explicit colors
      if (!attrs._hasExplicitColor) {
        graph.setEdgeAttribute(edgeKey, "color", defaultEdgeColor);
      }
    });

    // Also force a refresh to ensure reducers are re-applied
    sigma.refresh();
  }, [defaultNodeColor, defaultEdgeColor, themeColors.textColor, themeColors.secondaryBackgroundColor]);

  // Update node/edge reducers for hover highlighting and selection indication
  useEffect(() => {
    const sigma = sigmaRef.current;
    const graph = graphRef.current;
    if (!sigma || !graph) return;

    const selectedNodeId = currentSelection?.type === "node" ? currentSelection.id : null;
    const selectedEdgeId = currentSelection?.type === "edge" ? currentSelection.id : null;

    // Node reducer: apply theme colors and handle hover/selection
    sigma.setSetting("nodeReducer", (node, data): Partial<NodeDisplayData> => {
      const res: Partial<NodeDisplayData> = { ...data };
      const isSelected = node === selectedNodeId;
      const isHovered = node === hoveredNode;

      // The "focus" node is either the hovered or selected node
      const focusNode = hoveredNode || selectedNodeId;

      // Apply theme color if node doesn't have an explicit color
      const nodeColor = data.color || defaultNodeColor;
      res.color = nodeColor;

      // Selection indication: use highlighted ring and larger size
      if (isSelected) {
        res.highlighted = true;
        res.zIndex = 3;
        res.forceLabel = true;
        // Make selected node slightly larger
        res.size = (data.size ?? 8) * 1.3;
      } else if (isHovered) {
        res.highlighted = true;
        res.zIndex = 2;
        res.forceLabel = true;
      }

      // Handle focus state (hover or selection) for all nodes
      if (focusNode && !isHovered && !isSelected) {
        const neighbors = graph.neighbors(focusNode);
        if (neighbors.includes(node)) {
          // Neighbor nodes: bring to front
          res.zIndex = 1;
          res.forceLabel = true;
        } else {
          // Non-neighbor nodes: dim and push to back
          res.color = blendWithBackground(nodeColor, themeColors.secondaryBackgroundColor, 0.25);
          res.label = undefined;
          res.zIndex = 0;
        }
      }

      return res;
    });

    // Edge reducer: apply theme colors and handle hover/selection
    sigma.setSetting("edgeReducer", (edge, data): Partial<EdgeDisplayData> => {
      const res: Partial<EdgeDisplayData> = { ...data };
      const isSelectedEdge = edge === selectedEdgeId;

      // The "focus" node is either the hovered or selected node
      const focusNode = hoveredNode || selectedNodeId;

      // Apply theme color if edge doesn't have an explicit color
      const edgeColor = data.color || defaultEdgeColor;
      res.color = edgeColor;

      // Selection indication for edges
      if (isSelectedEdge) {
        res.color = themeColors.primaryColor;
        res.size = (data.size ?? 1) * 2;
      }

      // Handle edges when focusing a node (hover or selection)
      if (focusNode) {
        const [source, target] = graph.extremities(edge);
        if (source !== focusNode && target !== focusNode) {
          if (!isSelectedEdge) {
            // Dim non-connected edges
            res.color = blendWithBackground(edgeColor, themeColors.secondaryBackgroundColor, 0.15);
          }
        } else {
          // Connected edges: make slightly thicker
          res.size = (data.size ?? 1) * 1.5;
        }
      }

      return res;
    });

    sigma.refresh();
  }, [hoveredNode, currentSelection, themeColors.primaryColor, themeColors.secondaryBackgroundColor, defaultNodeColor, defaultEdgeColor]);

  // Container styles using CSS variables directly (browser resolves them, enabling theme detection)
  const containerStyle: React.CSSProperties = {
    width: width === "stretch" ? "100%" : `${width}px`,
    height: `${height}px`,
    backgroundColor: "var(--st-secondary-background-color, #f0f2f6)",
    borderRadius: "var(--st-base-radius, 0.5rem)",
    border: "1px solid var(--st-border-color, #d3d3d3)",
    overflow: "hidden",
    cursor: selectionEnabled ? "pointer" : "default",
  };

  return <div ref={containerRef} style={containerStyle} />;
};

export default SigmaGraph;
