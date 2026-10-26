from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.vector_store import clear_collection

router = APIRouter(tags=["Memory"])


class ClearMemoryRequest(BaseModel):
    agent: str
    user_id: str | None = None
    mode: str | None = None


@router.post("/memory/clear")
def clear_memory(req: ClearMemoryRequest):
    success = clear_collection(agent=req.agent, user_id=req.user_id, mode=req.mode)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear memory (best-effort)")
    return {"status": "ok"}
