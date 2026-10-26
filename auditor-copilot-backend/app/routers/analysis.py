from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.llm.llm_factory import get_llm
from app.agents.analysis_agent import AnalysisAgent
from app.schemas import AnalysisRequest
from fastapi import UploadFile, File
from typing import List
from app.utils.pdf_loader import load_document
from app.utils.validators import validate_file
from app.utils.vector_store import add_documents_to_store

router = APIRouter(tags=["Analysis"])

@router.post("/analysis/stream")
def stream_analysis(req: AnalysisRequest):
    llm = get_llm(req.llm_config, streaming=True)
    agent = AnalysisAgent(llm)

    def event_generator():
        try:
            for chunk in agent.stream(req.scenario, user_id=req.user_id):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {e}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.post("/analysis/ingest")
async def ingest_analysis_files(user_id: str, files: List[UploadFile] = File(...)):
    """Ingest files into temporary analysis memory for the provided user_id."""
    all_docs = []
    for file in files:
        validate_file(file.filename)
        content = await file.read()
        docs = load_document(content, file.filename)
        all_docs.extend(docs)

    add_documents_to_store(all_docs, agent="analysis_memory", user_id=user_id)

    return {"status": "ok", "files_ingested": [f.filename for f in files]}

"""
Analysis router for audit scenario streaming endpoint.
"""

# /analysis/stream streams audit analysis results using an LLM agent.
