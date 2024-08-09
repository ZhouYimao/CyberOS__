"""
agent 异步沟通；不求快，只求炫
加载thread

# TODO 
token超过多少多少，询问时光穿梭、新增或者从哪开始总结
# TODO
I now know the final answer.
Final answer: （应该把这些话都过滤了）
# TODO
不应当保存三元组至数据库
# TODO
尝试总结消息

# REST(userid, threadid, message) -> message
tools作为数组

"""
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 真正的代码

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver

from cyberos.settings.configs import ModelConfig, CYBEROS
from cyberos.memory.context import SYSTEM_MESSAGE


from cyberos.tool.ability import update_persona, update_core_memory, retrieve_memory, update_task

from cyberos.tool.skills.tools import web_search


USER_ID = "3367964d-5f5f-7008-1dd1dfa2e155"
THREAD_ID = 4
RDB_PATH = os.path.join(CYBEROS, "data", USER_ID, "test.sqlite")


config = {"configurable":{"thread_id": THREAD_ID, "user_id": USER_ID}} 

folder_path = os.path.dirname(RDB_PATH)
if not os.path.exists(folder_path):
    os.makedirs(folder_path) 
memory = SqliteSaver.from_conn_string(RDB_PATH)

tools = [update_persona,
        update_core_memory,
        retrieve_memory,
        web_search,
        update_task]

llm = ModelConfig().llm

graph = create_react_agent(model=llm, 
                           tools=tools, 
                           state_modifier=SYSTEM_MESSAGE,
                           checkpointer=memory)


for chunk in graph.stream(
    {"messages": [("human", "提醒我后天去看下牙")]},
    config,
    stream_mode="values",
):
    chunk["messages"][-1].pretty_print()

# snapshot = graph.get_state(config)

# print(snapshot)




"""
python react_agent.py 
================================ Human Message =================================

最冷的城市的天气是什么
================================== Ai Message ==================================

这个问题分为两部分。首先，我需要找出最冷的城市之一。然后，我应查询该城市的天气。我将先调用get_coolest_cities API 获取最冷城市列表。
Tool Calls:
  get_coolest_cities (call_51eea3c7-012c-4b12-81d3-999829522a0b)
 Call ID: call_51eea3c7-012c-4b12-81d3-999829522a0b
  Args:
================================= Tool Message =================================
Name: get_coolest_cities

nyc, sf
================================== Ai Message ==================================

Now I know that the coolest cities are New York City and San Francisco. I should find out the weather in these cities.
Tool Calls:
  get_weather (call_06814656-7226-4c47-a2a6-684927a27109)
 Call ID: call_06814656-7226-4c47-a2a6-684927a27109
  Args:
    location: nyc
================================= Tool Message =================================
Name: get_weather

It's 90 degrees and sunny.
================================== Ai Message ==================================

I can use get_weather.
Tool Calls:
  get_weather (call_528dc5ff-776e-4356-aaf7-a5bd6cbfead1)
 Call ID: call_528dc5ff-776e-4356-aaf7-a5bd6cbfead1
  Args:
    location: sf
================================= Tool Message =================================
Name: get_weather

It's 60 degrees and foggy.
================================== Ai Message ==================================

目前，旧金山的天气更冷一些，气温60度，多雾。纽约的天气则更热，气温90度，晴朗。但是旧金山的温度也取决于你对冷的定义，相对于纽约，60度可能对于你来说已经很冷了。
"""


"""
=============================== Human Message =================================

其实我23岁
================================== Ai Message ==================================

I can use update_core_memory.
Tool Calls:
  update_core_memory (call_5b11a7c6-b100-499e-a823-c2c25806ebe1)
 Call ID: call_5b11a7c6-b100-499e-a823-c2c25806ebe1
  Args:
    info: 年龄: 23
================================= Tool Message =================================
Name: update_core_memory

更新完毕
================================== Ai Message ==================================

I now know the final answer.
Final answer: 我已经更新了你的信息，周溢茂。你今年23岁，这个年纪正是一个充满活力和探索精神的时期。作为一个大学生，你正处在人生的黄金时期，有很多机会去学习新知识，探索新领域，挑战自我。如果你愿意，我们可以一起讨论更多关于你这个年龄段的话题，比如职业规划，人际关系，个人成长等等。期待与你一起分享更多有趣的事情！
"""