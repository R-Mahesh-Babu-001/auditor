from fastapi import APIRouter, HTTPException
from app.schemas import SOPFlowRequest
from app.agents.sop_flow_agent import SOPFlowAgent

router = APIRouter(tags=["SOP Flowchart"])

@router.post("/sop/flowchart")
async def generate_flowchart(req: SOPFlowRequest):
    try:
        agent = SOPFlowAgent()
        result = await agent.run(req.dict())

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# /sop/flowchart generates a flowchart from SOP text using the SOPFlowAgent.
