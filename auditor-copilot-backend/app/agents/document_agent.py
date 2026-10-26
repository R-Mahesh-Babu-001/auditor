from app.utils.vector_store import get_vector_store
from app.utils.streaming import stream_chat
from app.agents.base_agent import BaseAgent
from app.utils.memory import add_memory_text, get_recent_memory

CHART_POLICY = """
Core Rule — Chart Usage:
Do NOT create charts unless they are explicitly requested or clearly necessary to answer the question.
If the user requests a specific format (e.g., "table", "list", "text"), YOU MUST RESPECT THAT FORMAT AND NOT GENERATE A CHART.
If a chart is not required, respond with a normal textual audit-style answer.


Chart Generation Policy:
Apply the following rules only when a chart is explicitly or implicitly required by the user prompt or the provided data.
-Task (When a Chart Is Required)
-Generate a clean, structured JSON configuration compatible with React-based charting libraries such as Recharts or Chart.js.

Output Requirements:
Respond with valid JSON only

- Include only keys relevant to the selected chart type
- Do not include explanations outside the JSON
- Ensure all text is concise, professional, and audit-focused
- Line break and spacing for readability
- Do not include JavaScript, HTML, or comments
- Do not wrap the output in triple backticks or any code fence

JSON Structure
{{
  "chartType": "bar" | "line" | "pie" | "area" | "scatter" | "composed" | "radar",
  "data": [ <data item>, <data item>, ... ],
  "xKey": "<x-axis field name>",
  "yKey": "<single y-axis field name>",
  "yKeys": [ "<y1>", "<y2>", ... ],
  "title": "<brief and professional chart title>",
  "description": "<1–2 sentence explanation of what the chart represents, including assumptions if any>"
}}

Chart-Type-Specific Rules:
- Pie Chart
- Use "nameKey" instead of "xKey" (e.g., "category")

Scatter Chart
- Use "xKey" and "yKey" strictly as coordinate fields (e.g., "x", "y")

Radar Chart
- "xKey" = dimension or subject
- "yKey" = measured value

Composed Chart
- "yKey" → line series
- "yKeys" → bar and/or area series
"""

class DocumentAgent(BaseAgent):

    async def run(self, payload: dict) -> dict:
        question = payload["question"]
        vectordb = get_vector_store('DOCUMENT_ANALYSIS')
        try:
            docs = vectordb.similarity_search(question, k=5)
        except Exception:
            docs = []

        has_context = bool(docs)

        if has_context:
            context = "\n\n".join(d.page_content for d in docs)
            prompt = f"""
            You are an audit assistant.

            Answer the question using the context below.
            If the context is partially relevant, prefer it over general knowledge.

            {CHART_POLICY}

            Context:
            {context}

            Question:
            {question}
            """
        else:
            prompt = f"""
            You are an audit assistant.

            No relevant internal documents were found, acknowledge it and then;
            Answer the question using your general audit and business knowledge.
            Be clear, structured, and detailed.

            {CHART_POLICY}

            Question:
            {question}
            """

        response = await self.llm.ainvoke(prompt)

        # Optionally add Q&A to temporary conversation memory for document analysis
        try:
            user_id = payload.get("user_id")
            if user_id:
                add_memory_text(agent="document_memory", user_id=user_id, texts=[f"Q: {question}\nA: {response.content}"], mode=None)
        except Exception:
            pass

        return {
            "answer": response.content,
            "source": "kb" if has_context else "general_knowledge"
        }

    def stream(self, question: str, user_id: str | None = None):
        vectordb = get_vector_store('DOCUMENT_ANALYSIS')
        try:
            docs = vectordb.similarity_search(question, k=5)
        except Exception:
            docs = []

        has_context = bool(docs)
        context = ""
        if has_context:
            context = "\n\n".join(d.page_content for d in docs)

        # Inject conversation memory if available
        if user_id:
            try:
                # Retrieve conversation history relevant to the current question
                chat_history = get_recent_memory(agent="document_memory", user_id=user_id, query=question)
                if chat_history:
                    # Prepend recent Q&A to context or question
                    context = f"Previous Conversation Context:\n{chat_history}\n\nDocument Context:\n{context}"
            except Exception:
                pass

        if has_context:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an audit assistant. "
                        "Prefer the provided context over general knowledge.\n"
                        f"{CHART_POLICY}"
                    )
                },
                {
                    "role": "user",
                    "content": f"""
                    Context:
                    {context}

                    Question:
                    {question}
                    """
                }
            ]
        else:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an audit assistant. "
                        "No internal documents are available. "
                        "Answer using general audit and business knowledge.\n"
                        f"{CHART_POLICY}"
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]

        # Stream and accumulate response
        full_response = ""
        for chunk in stream_chat(self.llm, messages):
            full_response += chunk
            yield chunk

        # Persist conversation to memory
        if user_id and full_response:
            try:
                add_memory_text(agent="document_memory", user_id=user_id, texts=[f"Q: {question}", f"A: {full_response}"])
            except Exception:
                pass
