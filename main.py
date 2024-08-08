import os
from tool.tools import (
    extract_todo_item,
    update_core_memory, 
    retrieve_memory, 
    update_persona,
    web_search
)
from tool.ultilities import save_messages, system_message
from basic.base import MAX_MESSAGE_LENGTH, State, llm, CYBERLIFE
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
    SystemMessage,
    RemoveMessage
)
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import List, Dict, Any
from langgraph.prebuilt import ToolNode

# 这里想办法把用户名和他的 uuid 传进来
user_name =""
user_id = "3367964d-5f5f-7008-1dd1dfa2e155"
tools = [extract_todo_item,update_core_memory,update_persona,retrieve_memory,web_search]
config = {"configurable":{"thread_id": "1","user_name": user_name, "user_id": user_id}}  
llm = llm.bind_tools(tools)
tool_executor = ToolNode(tools)

memory = SqliteSaver.from_conn_string(os.path.join(CYBERLIFE, "database", user_name, "test.sqlite"))


def tools_router(state: State):
    return "action" if state["messages"][-1].tool_calls else END


def trim_router(state: State):
    return "save" if len(state["messages"]) > MAX_MESSAGE_LENGTH else "agent"


def call_model(state: State, config):
    return {"messages": [llm.invoke(state["messages"], config=config)]}


def call_tools(state: State):
    last_message = state["messages"][-1]
    res = tool_executor.invoke(state["messages"])

    for call in last_message.tool_calls:
        if call["name"] == "update_core_memory" or call["name"] == "update_persona":
            messages = state["messages"]
            messages[0] = SystemMessage(system_message())
            graph.update_state(config, {"messages": messages}, as_node="action")
            break

    return {"messages": res}


def trimmer(state: State):
    messages = state["messages"]
    print(f"Trimming {len(messages)} messages")
    return {"messages": [RemoveMessage(id=m.id) for m in messages[1:-4]]}


workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tools)
workflow.add_node("trim", trimmer)
workflow.add_node("save", save_messages)
workflow.add_conditional_edges(START, trim_router)
workflow.add_conditional_edges("agent", tools_router)
workflow.add_edge("action", "agent")
workflow.add_edge("save", "trim")
workflow.add_edge("trim", "agent")

graph = workflow.compile(checkpointer=memory, debug=False)

graph.invoke(
    {"messages": [SystemMessage(system_message())]},
    config=config
)


def chat_flow(message: str) -> List[Dict[str, Any]]:
    events = graph.stream({"messages": [HumanMessage(message)]}, config, stream_mode="updates")

    responses = []
    for event in events:
        for value in event.values():
            message = value["messages"][-1]
            if isinstance(message, AIMessage):
                response = {
                    "type": "ai_message",
                    "content": message.content
                }
                if message.additional_kwargs and 'tool_calls' in message.additional_kwargs:
                    response["tool_calls"] = [
                        {
                            "name": tool_call['function']['name'],
                            "arguments": tool_call['function']['arguments']
                        }
                        for tool_call in message.additional_kwargs['tool_calls']
                    ]
                responses.append(response)
            elif isinstance(message, ToolMessage):
                responses.append({
                    "type": "tool_result",
                    "content": message.content,
                    "tool_call_id": message.tool_call_id
                })
    return responses


if __name__ == "__main__":
    while True:
        user_input = input()
        if user_input == "/exit":
            break
        print(chat_flow(user_input))
        
