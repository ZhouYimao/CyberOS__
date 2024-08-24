"""
agent 异步沟通；不求快，只求炫
加载thread

# TODO 
token超过多少多少，询问时光穿梭、新增或者从哪开始总结
I now know the final answer.
Final answer: 

# REST(userid, threadid, message) -> message
tools作为数组

"""
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 真正的代码

from typing import Literal

from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from cyberos.settings.configs import ModelConfig, CYBEROS, USER_ID

from langgraph.checkpoint.sqlite import SqliteSaver

llm = ModelConfig().llm


THREAD_ID = 5
RDB_PATH = os.path.join(CYBEROS, "data", USER_ID, "test.sqlite")

config = {"configurable":{"thread_id": THREAD_ID, "user_id": USER_ID}} 

folder_path = os.path.dirname(RDB_PATH)
if not os.path.exists(folder_path):
    os.makedirs(folder_path) 
memory = SqliteSaver.from_conn_string(RDB_PATH)

def get_weather(location: str) -> str:
    """Call to get the current weather."""
    if location.lower() in ["sf", "san francisco"]:
        return "It's 60 degrees and foggy."
    else:
        return "It's 90 degrees and sunny."


def get_coolest_cities() -> str:
    """Get a list of coolest cities"""
    return "nyc, sf"

# Create the tool node with the tools
tools = [get_weather, get_coolest_cities]
tool_node = ToolNode(tools)

# Define the model with tools

llm_with_tools = llm.bind_tools(tools)

# Define the conditional edge between the nodes
def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "__end__"

# Define the model node
def call_model(state: MessagesState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge("__start__", "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
)
workflow.add_edge("tools", "agent")

app = workflow.compile(checkpointer=memory)
     

# example with a multiple tool calls in succession
for chunk in app.stream(
    {"messages": [("human", "最冷的城市的天气是什么")]},
    config,
    stream_mode="values",
):
    chunk["messages"][-1].pretty_print()

"""
================================ Human Message =================================

最冷的城市的天气是什么
================================== Ai Message ==================================

为了回答这个问题, 我首先需要调用 get_coolest_cities API 获取最冷的城市列表，然后用 get_weather API 查询该城市的天气。
Tool Calls:
  get_coolest_cities (call_1d06e8d1-8498-4256-b6e4-5c0df5c53c04)
 Call ID: call_1d06e8d1-8498-4256-b6e4-5c0df5c53c04
  Args:
================================= Tool Message =================================
Name: get_coolest_cities

nyc, sf
================================== Ai Message ==================================

I need to call get_weather for each city in the list from the get_coolest_cities call.
Tool Calls:
  get_weather (call_23104dae-34e0-45da-a671-a3ad8b0feb53)
 Call ID: call_23104dae-34e0-45da-a671-a3ad8b0feb53
  Args:
    location: nyc
================================= Tool Message =================================
Name: get_weather

It's 90 degrees and sunny.
================================== Ai Message ==================================

I can use get_weather.
Tool Calls:
  get_weather (call_a7e3ce28-1e94-46b1-aeda-97d371048ef6)
 Call ID: call_a7e3ce28-1e94-46b1-aeda-97d371048ef6
  Args:
    location: sf
================================= Tool Message =================================
Name: get_weather

It's 60 degrees and foggy.
================================== Ai Message ==================================

The weather in the two coldest cities are as follows: nyc: It's 90 degrees and sunny; sf: It's 60 degrees and foggy.
"""
     