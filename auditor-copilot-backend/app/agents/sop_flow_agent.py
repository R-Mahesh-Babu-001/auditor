from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.llm.gemini import get_fixed_llm

system_message = """
You are an AI that converts SOP documents into flowcharts in ReactFlow format.

Please analyze the following SOP content and create a flowchart representation using ReactFlow format.

Return ONLY a JSON object like:
{{
  "nodes": [
    {{
      "id": "unique_node_id",
      "type": "default",
      "position": {{ "x": 100, "y": 100 }},
      "data": {{ "label": "Step description" }},
      "style": {{ "background": "#fff", "border": "1px solid #ddd" }}
    }}
  ],
  "edges": [
    {{
      "id": "unique_edge_id",
      "source": "source_node_id",
      "target": "target_node_id",
      "type": "smoothstep",
      "animated": false
    }}
  ]
}}

Guidelines:
- Create nodes for each major step/decision in the SOP
- Use "input" for start, "output" for end, "default" for others
- Feel free to use styles(color, arrangement, border, edges,etc) to differentiate types of steps
- Limit to 50 nodes
- Include spacing (200–300px apart)
- Prefer expanding the flow chart both vertically and horizontally in equal or upto a reasonable ratio of proportions (Idealy use vertical blocks for Majot steps and expand with horizontal block to substeps and constraints )
- Include markerEnd arrows for flow direction
- Connect steps logically
- Do not add ```json ``` wrapper around the flow chart data

SOP Content:
"""

# - All the nodes should be part of a single flowchart, there should be only one pair of start and end point and everything should lie between them.


class SOPFlowAgent:

    def __init__(self):
        self.llm = get_fixed_llm()

    async def run(self, payload):
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{sop}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        result = await chain.ainvoke({

# SOPFlowAgent generates a ReactFlow-compatible flowchart from SOP text using an LLM.
# - run: returns a JSON flowchart structure for the given SOP content.
            "sop": payload["sop_text"]
        })

        return {"reactflow": result}
