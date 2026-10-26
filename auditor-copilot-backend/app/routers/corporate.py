from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from app.llm.llm_factory import get_llm
from app.agents.corporate_agent import CorporateAgent
from app.schemas import CorporateRequest
from typing import List
from app.utils.pdf_loader import load_document
from app.utils.validators import validate_file
from app.utils.vector_store import add_documents_to_store

router = APIRouter(tags=["Corporate"])

@router.post("/corporate/stream")
def stream_corporate_analysis(req: CorporateRequest):
    """
    Stream corporate analysis (guidelines or justification notes).
    """
    llm = get_llm(req.llm_config, streaming=True)
    agent = CorporateAgent(llm)

    def event_generator():
        try:
            for chunk in agent.stream(req.query, user_id=req.user_id):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {e}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.post("/corporate/ingest")
async def ingest_corporate_files(user_id: str, files: List[UploadFile] = File(...)):
    """
    Ingest files into temporary corporate memory for the provided user_id.
    """
    all_docs = []
    for file in files:
        validate_file(file.filename)
        content = await file.read()
        docs = load_document(content, file.filename)
        all_docs.extend(docs)

    add_documents_to_store(all_docs, agent="corporate_memory", user_id=user_id)

    return {"status": "ok", "files_ingested": [f.filename for f in files]}
