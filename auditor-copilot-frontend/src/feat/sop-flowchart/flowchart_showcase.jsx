
// SopFlowChartShowcaseScreen.jsx
// Displays a ReactFlow-based flowchart for SOP visualization.
import React, { useState } from "react";
import ReactFlow, { useNodesState, useEdgesState, MiniMap, Controls, Background, MarkerType } from "reactflow";
import "reactflow/dist/style.css";


/**
 * CustomNode
 * Renders a styled node for the SOP flowchart.
 */
const CustomNode = ({ data }) => {
    return (
        <div className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white p-4 rounded-2xl shadow-lg border border-white cursor-pointer hover:scale-105 transition-transform">
            <h4 className="font-bold">{data.label}</h4>
            {data.description && <p className="text-sm mt-1">{data.description}</p>}
        </div>
    );
};


// Register custom node type for ReactFlow
const nodeTypes = {
    customNode: CustomNode,
};



/**
 * SopFlowChartShowcaseScreen Component
 * Displays a ReactFlow-based flowchart for a given SOP (Standard Operating Procedure).
 * @param {Object} props
 * @param {Object} props.flow_data - Flowchart data with nodes and edges
 */
const SopFlowChartShowcaseScreen = ({ flow_data }) => {
    // State for flowchart data
    const [data, setData] = useState(flow_data);
    // ReactFlow state hooks for nodes and edges
    const [nodes, setNodes, onNodesChange] = useNodesState(data.nodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(data.edges);

    return (
        <div
            className="overflow-hidden"
            style={{ width: "100%", height: "100%", overflow: "hidden" }}
        >
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes} // Use custom node renderer
                panOnDrag={true}
                panOnScroll={true}
                nodesDraggable={true}
                proOptions={{ hideAttribution: true }}
                nodesConnectable={true}
                minZoom={0.1}
                maxZoom={3}
                style={{ background: "#f0f0f0" }}
                className="w-full h-full overflow-hidden"
            >
                <MiniMap nodeColor={(node) => "#8b5cf6"} />
                <Controls />
                <Background color="#aaa" gap={16} />
            </ReactFlow>
        </div>
    );
};

export default SopFlowChartShowcaseScreen;