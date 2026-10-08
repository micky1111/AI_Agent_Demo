"""Core agent loop: interprets a natural-language instruction, decides which
tool(s) to call (search the knowledge base, look up or update an
apartment's live status, create a task), executes them, and returns the
model's final response.

Write actions (update_apartment_status, create_task) prompt for
confirmation before executing, unless --yes/-y is passed.

Run directly: `uv run python src/agent.py "Update unit SM-012 to sold"`
"""

import sys

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from tools.firebase_ops import create_task, get_apartment_status, update_apartment_status
from tools.search_docs import search_knowledge_base

MODEL = "gpt-4o-mini"
MAX_STEPS = 6

SYSTEM_PROMPT = (
    "You are the Company Brain agent for a fictional real estate developer. "
    "All data you work with is synthetic/fictional. Use search_knowledge_base "
    "to answer general questions about pricing, policies, specs, amenities, "
    "etc. Unit identifiers follow the format 'SM-0NN' (e.g. 'SM-012') as "
    "used in the price list — if the user gives a bare number or an "
    "ambiguous reference without this format, ask them to confirm the full "
    "unit code rather than guessing. For a unit's CURRENT status, use "
    "get_apartment_status (Firestore is the live source of truth, not the "
    "static knowledge base). Use update_apartment_status when asked to "
    "change a unit's status (e.g. to Sold, Available, or Reserved). Use "
    "create_task when asked to create a follow-up task. After calling a "
    "tool, summarize what happened in a short confirmation to the user."
)

TOOLS = [search_knowledge_base, get_apartment_status, update_apartment_status, create_task]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}
WRITE_TOOLS = {"update_apartment_status", "create_task"}

DEMO_INSTRUCTION = "What is the cancellation policy?"


def _confirm(call_name: str, call_args: dict) -> bool:
    answer = (
        input(f"\nAgent wants to call {call_name}({call_args}). Proceed? [y/N]: ")
        .strip()
        .lower()
    )
    return answer in ("y", "yes")


def _execute_tool(call: dict, auto_confirm: bool) -> str:
    tool_fn = TOOLS_BY_NAME.get(call["name"])
    if tool_fn is None:
        return f"Error: unknown tool '{call['name']}'."

    if call["name"] in WRITE_TOOLS and not auto_confirm:
        if not _confirm(call["name"], call["args"]):
            return "Cancelled by user — write not performed."

    try:
        return tool_fn.invoke(call["args"])
    except Exception as e:
        return f"Error calling {call['name']}: {e}"


def run(instruction: str, auto_confirm: bool = False) -> str:
    llm = ChatOpenAI(model=MODEL, temperature=0).bind_tools(TOOLS)
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(instruction)]

    response = llm.invoke(messages)
    messages.append(response)

    steps = 0
    while response.tool_calls:
        steps += 1
        if steps > MAX_STEPS:
            return (
                f"Stopped after {MAX_STEPS} tool-call steps without a final "
                "answer — this may indicate the agent got stuck in a loop."
            )
        for call in response.tool_calls:
            result = _execute_tool(call, auto_confirm)
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
        response = llm.invoke(messages)
        messages.append(response)

    return response.content


def main() -> None:
    args = sys.argv[1:]
    auto_confirm = any(a in ("--yes", "-y") for a in args)
    args = [a for a in args if a not in ("--yes", "-y")]
    instruction = " ".join(args) or DEMO_INSTRUCTION

    print(f"Instruction: {instruction}\n")
    print(run(instruction, auto_confirm=auto_confirm))


if __name__ == "__main__":
    main()
