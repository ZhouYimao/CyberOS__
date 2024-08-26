import sys
import os
import asyncio  # 添加 asyncio 以支持异步调用

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

# 真正的代码
from cyberos.settings.configs import ModelConfig
from typing import Literal
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

POSTGRESQL_CONFIG = {
    'dbname': 'langgraph_test',
    'user': 'cyberlife_os',
    'password': 'cyberlife2024',
    'host': 'localhost',
    'port': 5432
}

# 构建连接字符串
DB_URI = f"postgresql://{POSTGRESQL_CONFIG['user']}:{POSTGRESQL_CONFIG['password']}@{POSTGRESQL_CONFIG['host']}:{POSTGRESQL_CONFIG['port']}/{POSTGRESQL_CONFIG['dbname']}"

@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        raise AssertionError("Unknown city")

tools = [get_weather]
model = ModelConfig().llm

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
    "row_factory": dict_row,
}

# 创建一个异步函数来运行异步代码
async def main():
    async with AsyncConnectionPool(
        # Example configuration
        conninfo=DB_URI,
        max_size=20,
        kwargs=connection_kwargs,
    ) as pool, pool.connection() as conn:
        checkpointer = AsyncPostgresSaver(conn)

        # NOTE: you need to call .setup() the first time you're using your checkpointer
        await checkpointer.setup()

        graph = create_react_agent(model, tools=tools, checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "4"}}
        res = await graph.ainvoke(
            {"messages": [("human", "what's the weather in nyc")]}, config
        )

        checkpoint = await checkpointer.aget(config)
        print(checkpoint)


# 启动异步函数
if __name__ == "__main__":
    asyncio.run(main())