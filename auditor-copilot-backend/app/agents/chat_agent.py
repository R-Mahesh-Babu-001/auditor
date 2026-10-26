from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.agents.base_agent import BaseAgent
from app.utils.streaming import stream_chat
from app.utils.memory import get_recent_memory, add_memory_text
from app.utils.prompts import get_prompt

chat_agent_system_message = """
Role & Professional Standards:
- You are a Senior Internal Audit Auditor Agent operating in accordance with:
- IIA International Professional Practices Framework (IPPF)
- COSO Internal Control – Integrated Framework
- Sarbanes-Oxley Act (SOX), including ICFR requirements
- You apply sound professional judgment, skepticism, and independence when analyzing information, forming conclusions, and communicating results.

Core Operating Principles:
- Prioritize governance, risk management, and internal control effectiveness
- Maintain objectivity, accuracy, and audit defensibility
- Align all conclusions with control objectives, risk assessment, and evidence
- Avoid unnecessary complexity or visualizations that do not enhance audit understanding

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

Handling Ambiguity
- If the user request is ambiguous:
- Make reasonable audit-based assumptions
- Clearly document those assumptions in the "description" field

Behavioral Guidance
- Maintain professional audit judgment
- Prioritize clarity, accuracy, and relevance
- Never generate charts by default
- Follow chart rules only when a chart is truly required

Context & Conversation Awareness

Given the context and conversation
"""


class ChatAgent(BaseAgent):
    def __init__(self, llm):
        self.llm = llm

    def stream(self, messages: list):
        """
        Generator yielding response chunks.
        """
        # Optionally inject memory if messages contain user_id metadata in the first element
        user_id = None
        if messages and isinstance(messages[0], dict):
            user_id = messages[0].get("user_id")

        if user_id:
            memory = get_recent_memory(agent="chat_memory", user_id=user_id)
            if memory:
                # prepend system context
                sys_prompt = get_prompt("chat", "system") or f"Conversation memory:\n{memory}"
                messages = [
                    {"role": "system", "content": chat_agent_system_message},
                    {"role": "system", "content": f"Conversation memory:\n{memory}"}
                ] + messages

        # capture user question
        user_text = None
        for m in messages:
            if m.get("role") == "user":
                user_text = m.get("content")
                break

        assistant_buffer = ""

        for chunk in stream_chat(self.llm, messages):
            # stream out to caller
            yield chunk

            # accumulate for memory persistence
            try:
                assistant_buffer += chunk
            except Exception:
                pass

        # After streaming completes, persist Q/A into chat memory as separate entries (best-effort)
        if user_id and user_text and assistant_buffer:
            try:
                add_memory_text(agent="chat_memory", user_id=user_id, texts=[f"USER: {user_text}", f"ASSISTANT: {assistant_buffer}"])
            except Exception:
                pass

    async def run(self, payload):
        prompt = ChatPromptTemplate.from_messages([
            ("system", chat_agent_system_message),
            ("human", "{question}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        # Inject memory into prompt
        memory = ""
        if payload.get("user_id"):
            memory = get_recent_memory(agent="chat_memory", user_id=payload.get("user_id"))

        question = payload["query"]
        if memory:
            question = f"Memory:\n{memory}\n\nUser Question:\n{question}"

        response = await chain.ainvoke({
            "question": question
        })

        # Extract response text
        if isinstance(response, str):
            resp_text = response
        else:
            resp_text = getattr(response, "content", str(response))

        # Persist to memory (best-effort)
        try:
            if payload.get("user_id"):
                add_memory_text(agent="chat_memory", user_id=payload.get("user_id"), texts=[f"USER: {payload.get('query')}", f"ASSISTANT: {resp_text}"])
        except Exception:
            pass

        return {
            "answer": resp_text,
            "confidence": 0.9
        }
