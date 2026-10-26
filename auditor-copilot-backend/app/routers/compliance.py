from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.llm.llm_factory import get_llm
from app.agents.compliance_agent import ComplianceAgent
from app.schemas import ComplianceRequest

router = APIRouter(tags=["Compliance"])


@router.post("/compliance/stream")
def stream_compliance(req: ComplianceRequest):
    llm = get_llm(req.llm_config, streaming=True)
    agent = ComplianceAgent(llm, mode=(req.mode or "IT"))

    def event_generator():
        try:
            for chunk in agent.stream(req.query, user_id=req.user_id):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {e}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/compliance/run")
async def run_compliance(req: ComplianceRequest):
    llm = get_llm(req.llm_config, streaming=False)
    agent = ComplianceAgent(llm, mode=(req.mode or "IT"))
    return await agent.run(req.dict())
