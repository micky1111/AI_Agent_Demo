"""Core agent loop: interprets a natural-language instruction, decides which
tool(s) to call (search the knowledge base, update an apartment's status,
create a task), executes them, and returns the model's final response.

Run directly: `uv run python src/agent.py "Update apartment 12 to sold"`
"""

import sys

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from tools.firebase_ops import create_task, update_apartment_status
from tools.search_docs import search_knowledge_base

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are the Company Brain agent for a fictional real estate developer. "
    "All data you work with is synthetic/fictional. Use search_knowledge_base "
    "to answer questions about pricing, policies, specs, amenities, etc. Use "
    "update_apartment_status when asked to change an apartment/unit's status "
    "(e.g. to Sold, Available, or Reserved). Use create_task when asked to "
    "create a follow-up task. After calling a tool, summarize what happened "
    "in a short confirmation to the user."
)

TOOLS = [search_knowledge_base, update_apartment_status, create_task]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}

DEMO_INSTRUCTION = "What is the cancellation policy?"


def run(instruction: str) -> str:
    llm = ChatOpenAI(model=MODEL, temperature=0).bind_tools(TOOLS)
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(instruction)]

    response = llm.invoke(messages)
    messages.append(response)

    while response.tool_calls:
        for call in response.tool_calls:
            tool_fn = TOOLS_BY_NAME[call["name"]]
            result = tool_fn.invoke(call["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
        response = llm.invoke(messages)
        messages.append(response)

    return response.content


def main() -> None:
    instruction = " ".join(sys.argv[1:]) or DEMO_INSTRUCTION
    print(f"Instruction: {instruction}\n")
    print(run(instruction))


if __name__ == "__main__":
    main()
