import { useState, useCallback } from "react";
import { ExtractedResult } from "./use-file-extractor";
import { useSopFlowchartApi } from "./useSopFlowchartApi";

/* ---------- ReactFlow Types (unchanged) ---------- */

export interface ReactFlowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: { label: string };
  style?: Record<string, any>;
}

export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
  label?: string;
  markerStart?: string;
  markerEnd?: string;
}

export interface ReactFlowData {
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
}

/* ---------- Hook ---------- */

export const useSopFlowchartGenerator = () => {
  const [flowData, setFlowData] = useState<ReactFlowData | null>(null);

  const {
    generateFlowchartFromSop,
    loading,
    error,
  } = useSopFlowchartApi();

  /* ---------- Validation & Enhancement (UNCHANGED) ---------- */

  const validateAndEnhanceReactflowData = (data: any): ReactFlowData => {
    if (!data || typeof data !== "object") {
      return { nodes: [], edges: [] };
    }

    const nodes = Array.isArray(data.nodes) ? data.nodes : [];
    const edges = Array.isArray(data.edges) ? data.edges : [];

    const enhancedNodes: ReactFlowNode[] = nodes.map((node: any, i: number) => {
      const id = node.id || `node_${i}`;
      const type = node.type || "default";
      const position = node.position || { x: 100 + i * 220, y: 100 + i * 120 };
      const dataObj = node.data || { label: `Step ${i + 1}` };

      let style = node.style;
      if (!style) {
        if (type === "input") {
          style = {
            background: "#e1f5fe",
            border: "2px solid #0277bd",
            borderRadius: "8px",
            padding: "10px",
          };
        } else if (type === "output") {
          style = {
            background: "#e8f5e8",
            border: "2px solid #388e3c",
            borderRadius: "8px",
            padding: "10px",
          };
        } else {
          style = {
            background: "#fff",
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "10px",
          };
        }
      }

      return { id, type, position, data: dataObj, style };
    });

    const validNodeIds = new Set(enhancedNodes.map((n) => n.id));
    const enhancedEdges: ReactFlowEdge[] = edges
      .filter(
        (e: any) => validNodeIds.has(e.source) && validNodeIds.has(e.target)
      )
      .map((e: any, i: number) => ({
        id: e.id || `edge_${i}`,
        source: e.source,
        target: e.target,
        type: e.type || "smoothstep",
        animated: e.animated ?? false,
        label: e.label,
        markerEnd: "arrowclosed",
      }));

    return { nodes: enhancedNodes, edges: enhancedEdges };
  };

  /* ---------- Generator ---------- */

  const generateFlowchart = useCallback(
    async (extracted: ExtractedResult) => {
      if (!extracted?.content || typeof extracted.content !== "string") {
        throw new Error("Invalid extracted content");
      }

      const rawFlow = await generateFlowchartFromSop(extracted.content);
      if (!rawFlow) return null;

      const enhanced = validateAndEnhanceReactflowData(rawFlow);
      setFlowData(enhanced);
      return enhanced;
    },
    [generateFlowchartFromSop]
  );

  return {
    generateFlowchart,
    flowData,
    loading,
    error,
  };
};
