from langchain.agents import create_agent
from app.utils.search_tool import get_search_tool
from app.agents.base_agent import BaseAgent
from app.utils.streaming import stream_chat
from app.utils.memory import get_recent_memory, add_memory_text
from app.utils.prompts import get_prompt


class AnalysisAgent(BaseAgent):
    """
    Executes audit analysis scenarios.
    Capable of using tools (web search).
    """
    def __init__(self, llm):
        self.llm = llm

    def stream(self, scenario: str, user_id: str | None = None):
        # Inject memory if user_id is provideduh byb 
        input_text = scenario
        if user_id:
            # Retrieve context relevant to the current scenario (files + chat history)
            mem = get_recent_memory(agent="analysis_memory", user_id=user_id, query=scenario)
            if mem:
                input_text = f"Context from uploaded documents and history:\n{mem}\n\nScenario/Query:\n{scenario}"

        # If scenario suggests a justification-style analysis, stream structured sections one-by-one
        lower = scenario.lower() if isinstance(scenario, str) else ""
        justification_keywords = ["justification", "variance", "explanation", "justification notes"]
        
        full_response = ""

        if any(k in lower for k in justification_keywords):
            sections = [
                "observation",
                "root_cause",
                "management_explanation",
                "auditor_assessment",
                "risk_rating",
                "recommendation",
            ]

            sys_prompt = get_prompt("analysis", "system") or "You are an audit analyst producing one section of a structured justification output. Respond only with the requested section content."

            for sec in sections:
                messages = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f"Produce the '{sec}' section for the following scenario:\n\n{input_text}"}
                ]

                for chunk in stream_chat(self.llm, messages):
                    full_response += chunk
                    yield chunk
        else:
            messages = [{"role": "user", "content": input_text}]
            for chunk in stream_chat(self.llm, messages):
                full_response += chunk
                yield chunk
        
        # Persist conversation to memory
        if user_id and full_response:
            try:
                add_memory_text(agent="analysis_memory", user_id=user_id, texts=[f"QUERY: {scenario}", f"ANALYSIS: {full_response}"])
            except Exception:
                pass

    async def run(self, payload: dict) -> dict:
        tools = [get_search_tool()]

        agent = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=(
                "You are an expert audit analyst. "
                "Use tools when needed. "
                "Provide structured, evidence-backed analysis."
            )
        )

        input_text = payload["scenario"]
        if payload.get("user_id"):
            mem = get_recent_memory(agent="analysis_memory", user_id=payload.get("user_id"))
            if mem:
                input_text = f"Memory:\n{mem}\n\nScenario:\n{input_text}"

        result = await agent.ainvoke({"messages": [{"role": "user", "content": input_text}]})

        return {
            "analysis": result["messages"][-1].content
        }


# AnalysisAgent executes audit analysis scenarios using an LLM and optional web search tools.
# - stream: streams LLM responses for a scenario.
# - run: runs the agent asynchronously and returns structured analysis.