from langchain_core.messages import HumanMessage, AIMessage

# def stream_chat(llm, messages: list):
#     """
#     Streams tokens from an LLM based on conversation history.
#     """
#     lc_messages = []

#     for m in messages:
#         if m["role"] == "user":
#             lc_messages.append(HumanMessage(content=m["content"]))
#         else:
#             lc_messages.append(AIMessage(content=m["content"]))

#     for chunk in llm.stream(lc_messages):
#         if chunk.content:
#             yield chunk.content


def stream_chat(llm, messages: list):
    """
    Streams clean, markdown-safe text chunks from an LLM.
    Preserves formatting, lists, headers, and spacing.
    """

    lc_messages = []
    for m in messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))

    buffer = ""

    for chunk in llm.stream(lc_messages):
        delta = chunk.content or ""
        if not delta:
            continue

        buffer += delta

        # ✅ Flush ONLY on paragraph boundaries
        if "\n\n" in buffer:
            parts = buffer.split("\n\n")
            for part in parts[:-1]:
                yield part + "\n"
            buffer = parts[-1]

    # Flush remaining content
    if buffer.strip():
        yield buffer

"""
Streaming utility for LLM chat responses, preserving markdown formatting.
"""

# stream_chat streams LLM output in markdown-safe chunks, flushing on paragraph boundaries.