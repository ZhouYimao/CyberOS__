import os
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.tools.tavily_search import TavilySearchResults

# set up API key
os.environ["TAVILY_API_KEY"] = "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"

# set up the agent
llm = ChatOpenAI(
    model="qwen2-instruct",
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8011/v1",
    temperature=0,
)
search = TavilySearchAPIWrapper()
tavily_tool = TavilySearchResults(api_wrapper=search)

# initialize the agent
agent_chain = initialize_agent(
    [tavily_tool],
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# run the agent
print(agent_chain.run(
    "周溢茂是谁",
))