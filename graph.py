from typing import (
    Optional,
    Sequence,
    Union
)

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    RemoveMessage,
)
from langchain_core.tools import BaseTool
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.constants import START
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.prebuilt.tool_node import ToolNode


def create_custom_graph(
        model: BaseChatModel,
        tools: Union[ToolExecutor, Sequence[BaseTool]],
        state: AgentState = None,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        interrupt_before: Optional[Sequence[str]] = None,
        interrupt_after: Optional[Sequence[str]] = None,
        debug: bool = False,
) -> CompiledGraph:
    if state is None:
        state = AgentState()

    llm = model.bind_tools(tools)
    tool_executor = ToolNode(tools)

    def tools_router(state):
        return "action" if state["messages"][-1].tool_calls else END

    def trim_router(state):
        return "save" if len(state["messages"]) > MAX_MESSAGE_LENGTH else "agent"

    def call_model(state, config):
        return {"messages": [llm.invoke(state["messages"], config=config)]}

    def call_tools(state):
        last_message = state["messages"][-1]
        res = tool_executor.invoke(state["messages"])

        # for call in last_message.tool_calls:
        #     if call["name"] == "update_core_memory" or call["name"] == "update_persona":
        #         messages = state["messages"]
        #         messages[0] = SystemMessage(system_message())
        #         graph.update_state(config, {"messages": messages}, as_node="action")
        #         break

        return {"messages": res}

    def trimmer(state):
        messages = state["messages"]
        print(f"Trimming {len(messages)} messages")
        return {"messages": [RemoveMessage(id=m.id) for m in messages[1:-4]]}

    workflow = StateGraph(state)
    workflow.add_node("agent", call_model)
    workflow.add_node("action", call_tools)
    workflow.add_node("trim", trimmer)
    workflow.add_node("save", save_messages)
    workflow.add_conditional_edges(START, trim_router)
    workflow.add_conditional_edges("agent", tools_router)
    workflow.add_edge("action", "agent")
    workflow.add_edge("save", "trim")
    workflow.add_edge("trim", "agent")

    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_before,
        interrupt_after=interrupt_after,
        debug=debug
    )
