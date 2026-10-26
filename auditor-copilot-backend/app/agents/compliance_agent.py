from app.agents.base_agent import BaseAgent
from app.utils.streaming import stream_chat
from app.utils.memory import get_recent_memory, add_memory_text


class ComplianceAgent(BaseAgent):
    """Compliance Audit Agent supporting mode-based behavior."""
    MODES = {
        "IT": "IT Compliance",
        "FINANCE": "Finance & Accounting Compliance"
    }

    def __init__(self, llm, mode: str = "IT"):
        self.llm = llm
        self.mode = mode if mode in self.MODES else "IT"

    def _system_instructions(self) -> str:
        from app.utils.prompts import get_prompt

        tpl = get_prompt("compliance", "system")
        if tpl:
            return tpl

        if self.mode == "FINANCE":
            return "You are a Finance & Accounting compliance auditor. Focus on SOX, GAAP, and control effectiveness."
        return "You are an IT compliance auditor. Focus on access controls, change management, and ITGCs."

    def stream(self, query: str, user_id: str | None = None):
        messages = [
            {"role": "system", "content": self._system_instructions()},
            {"role": "user", "content": query}
        ]

        # Inject mode-scoped memory
        if user_id:
            mem = get_recent_memory(agent="compliance_memory", user_id=user_id, mode=self.mode)
            if mem:
                messages.insert(1, {"role": "system", "content": f"Mode memory:\n{mem}"})

        yield from stream_chat(self.llm, messages)

    async def run(self, payload: dict) -> dict:
        query = payload.get("query")
        user_id = payload.get("user_id")

        mem = ""
        if user_id:
            mem = get_recent_memory(agent="compliance_memory", user_id=user_id, mode=self.mode)

        prompt = f"{self._system_instructions()}\n\n"
        if mem:
            prompt += f"Memory:\n{mem}\n\n"

        prompt += f"Query:\n{query}"

        response = await self.llm.ainvoke(prompt)

        # store short Q&A into memory
        try:
            if user_id:
                add_memory_text(agent="compliance_memory", user_id=user_id, texts=[f"Q: {query}\nA: {response.content}"], mode=self.mode)
        except Exception:
            pass

        return {"answer": response.content, "mode": self.mode}
