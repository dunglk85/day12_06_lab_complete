from __future__ import annotations

from pathlib import Path
from typing import Annotated

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from agent.config import load_settings
from agent.policy import extract_trip_intent, should_force_parallel_search
from agent.tools import calculate_budget, search_flights, search_hotels

BASE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT = (BASE_DIR / "system_prompt.txt").read_text(encoding="utf-8")


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


tools_list = [search_flights, search_hotels, calculate_budget]


settings = load_settings()
llm = ChatOpenAI(model=settings.model_name)
llm_with_tools = llm.bind_tools(tools_list)


def agent_node(state: AgentState):
    messages = state["messages"]

    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    has_tool_results = any(isinstance(msg, ToolMessage) for msg in messages)
    if has_tool_results:
        response = llm.invoke(messages)
        print("Trả lời trực tiếp")
        return {"messages": [response]}

    last_human = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_human = msg.content
            break

    if should_force_parallel_search(last_human):
        intent = extract_trip_intent(last_human)
        tool_calls = [
            {
                "name": "search_flights",
                "args": {"origin": intent.origin, "destination": intent.destination},
                "id": "call_flights",
                "type": "tool_call",
            },
            {
                "name": "search_hotels",
                "args": {"city": intent.destination},
                "id": "call_hotels",
                "type": "tool_call",
            },
        ]
        response = AIMessage(content="", tool_calls=tool_calls)
    else:
        response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"Gọi tool: {tc['name']} ({tc['args']})")
    else:
        print("Trả lời trực tiếp")

    return {"messages": [response]}


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)

    tool_node = ToolNode(tools_list)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    builder.add_edge("agent", END)

    return builder.compile()