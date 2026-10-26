from fastapi import APIRouter, HTTPException
from app.schemas import DocumentQueryRequest
from app.llm.llm_factory import get_llm
from app.agents.document_agent import DocumentAgent

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import List

from app.utils.pdf_loader import load_document
from app.utils.validators import validate_file
from app.utils.vector_store import add_documents_to_store


router = APIRouter(tags=["Document Analysis"])

@router.post("/documents/query/stream")
def stream_document_query(req: DocumentQueryRequest):
    llm = get_llm(req.llm_config, streaming=True)
    agent = DocumentAgent(llm)

    def event_generator():
        try:
            for chunk in agent.stream(req.question, user_id=req.user_id):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {e}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.post("/documents/ingest")
async def ingest_documents(files: List[UploadFile] = File(...)):
    try:
        all_docs = []

        for file in files:
            validate_file(file.filename)
            content = await file.read()

            docs = load_document(content, file.filename)
            all_docs.extend(docs)

        # Persist into DOCUMENT_ANALYSIS collection
        add_documents_to_store(all_docs, collection_name='DOCUMENT_ANALYSIS')

        return {
            "status": "success",
            "files_ingested": [file.filename for file in files],
            "documents_added": len(all_docs)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
Document analysis router for document query and ingestion endpoints.
"""

# /documents/query/stream streams answers to document-related questions using the LLM and vector store.
# /documents/ingest uploads and indexes documents for analysis.
