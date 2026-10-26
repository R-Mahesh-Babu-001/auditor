from app.agents.base_agent import BaseAgent
from app.utils.streaming import stream_chat
from app.utils.memory import get_recent_memory, add_memory_text
from app.utils.prompts import get_prompt

class CorporateAgent(BaseAgent):
    """
    Agent for Corporate Accounting Guidelines and Justification Notes analysis.
    """
    def __init__(self, llm):
        self.llm = llm

    def stream(self, query: str, user_id: str | None = None):
        input_text = query
        if user_id:
            # Retrieve context relevant to the current query (files + chat history)
            mem = get_recent_memory(agent="corporate_memory", user_id=user_id, query=query)
            if mem:
                input_text = f"Context from uploaded documents and history:\n{mem}\n\nQuery:\n{query}"

        lower_query = query.lower()
        justification_keywords = ["justification", "variance", "explanation", "justification note"]
        
        full_response = ""
        sys_prompt = get_prompt("corporate", "system") or "You are a corporate auditor. Provide structured, evidence-backed analysis."

        if any(k in lower_query for k in justification_keywords):
            # Special structured output for justification notes
            sections = [
                "observation",
                "root_cause",
                "management_explanation",
                "auditor_assessment",
                "risk_rating",
                "recommendation",
            ]

            for sec in sections:
                messages = [
                    {"role": "system", "content": f"{sys_prompt}\n\nProduce ONLY the '{sec}' section."},
                    {"role": "user", "content": input_text}
                ]

                for chunk in stream_chat(self.llm, messages):
                    full_response += chunk
                    yield chunk
                
                # Add a small separator between sections for readability in streaming
                yield "\n\n"
        else:
            # General corporate guideline analysis
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": input_text}
            ]
            for chunk in stream_chat(self.llm, messages):
                full_response += chunk
                yield chunk
        
        # Persist conversation to memory
        if user_id and full_response:
            try:
                add_memory_text(agent="corporate_memory", user_id=user_id, texts=[f"QUERY: {query}", f"ANALYSIS: {full_response}"])
            except Exception:
                pass

    async def run(self, payload: dict) -> dict:
        query = payload.get("query")
        user_id = payload.get("user_id")

        input_text = query
        if user_id:
            mem = get_recent_memory(agent="corporate_memory", user_id=user_id, query=query)
            if mem:
                input_text = f"Memory:\n{mem}\n\nQuery:\n{query}"

        sys_prompt = get_prompt("corporate", "system") or "You are a corporate auditor."
        
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": input_text}
        ]

        # Use non-streaming invoke for 'run'
        response = await self.llm.ainvoke(messages)
        full_answer = response.content

        # store short Q&A into memory
        if user_id:
            try:
                add_memory_text(agent="corporate_memory", user_id=user_id, texts=[f"Q: {query}\nA: {full_answer}"])
            except Exception:
                pass

        return {"answer": full_answer}
