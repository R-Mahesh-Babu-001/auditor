from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.llm.llm_factory import get_llm
from app.agents.chat_agent import ChatAgent
from app.schemas import ChatRequest
from fastapi import UploadFile, File
from typing import List
from app.utils.pdf_loader import load_document
from app.utils.validators import validate_file
from app.utils.memory import add_memory_text
from app.utils.vector_store import add_documents_to_store

router = APIRouter(tags=["Chat"])

# @router.post("/chat")
# async def chat(req: ChatRequest):
#     llm = get_llm(req.model_config)
#     agent = ChatAgent(llm)
#     return await agent.run(req.dict())

@router.post("/chat/stream")
def stream_chat_response(req: ChatRequest):
    llm = get_llm(req.llm_config, streaming=True)
    agent = ChatAgent(llm)

    def event_generator():
        messages = [{"role": "user", "content": req.query}]
        if getattr(req, "user_id", None):
            messages[0]["user_id"] = req.user_id
        try:
            for chunk in agent.stream(messages):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {e}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.post("/chat/ingest")
async def ingest_chat_files(user_id: str, files: List[UploadFile] = File(...)):
    """Ingest files into temporary chat memory for the provided user_id."""
    all_docs = []
    for file in files:
        validate_file(file.filename)
        content = await file.read()
        docs = load_document(content, file.filename)
        all_docs.extend(docs)

    # store into chat-specific memory namespace for this user
    add_documents_to_store(all_docs, agent="chat_memory", user_id=user_id)

    return {"status": "ok", "files_ingested": [f.filename for f in files]}

"""
Chat router for streaming chat responses from the LLM agent.
"""

# /chat/stream streams chat responses for a given user query.
