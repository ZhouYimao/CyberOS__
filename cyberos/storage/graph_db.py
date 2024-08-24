import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

# 真正的代码如下
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import re

from llama_index.core import Settings, Document

from llama_index.core import PropertyGraphIndex
from llama_index.core.indices.property_graph import (
    LLMSynonymRetriever,
    VectorContextRetriever,
)

from llama_index.llms.langchain import LangChainLLM
from llama_index.embeddings.langchain import LangchainEmbedding

from cyberos.settings.configs import ModelConfig, DatabaseConfig
from cyberos.settings.prompts import GRAPH_SUMMARY_PROMPT

PLACE = "南昌"

# 初始化配置
model_config = ModelConfig()
db_config = DatabaseConfig()

lc_llm = ModelConfig().llm
Settings.llm = LangChainLLM(llm=lc_llm)

emb = ModelConfig().embed_model

Settings.embed_model = LangchainEmbedding(emb)

graph_store = DatabaseConfig().graph_store

index = PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,
)


def get_current_time():
    current_utc_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    east_8_tz = timezone(timedelta(hours=8))
    current_time = current_utc_time.astimezone(east_8_tz)
    return current_time, int(current_utc_time.timestamp())


def generate_summary(text: str) -> str:
    summary_prompt = GRAPH_SUMMARY_PROMPT.format(
        PLACE=PLACE,
        text=text
    )

    # Use the LLM to generate the summary
    summary = Settings.llm.complete(summary_prompt)
    return summary.text


def graphlize_messages(messages: List[Dict[str, str]]):
    """
    Convert chat messages to graph database triples.
    """
    current_time, timestamp = get_current_time()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    text = f"对话发生在：{formatted_time}\n"
    for message in messages:
        text += f"{message['role']}: {message['content']}\n"
    summary = generate_summary(text)
    document = Document(text=summary)
    index.insert(document)


def retrieve(query: str):
    """
    Retrieve and print relevant information from the graph database based on the query,
    outputting only the triplets.
    """

    llm_synonym = LLMSynonymRetriever(
        index.property_graph_store,
        include_text=True,
    )
    vector_context = VectorContextRetriever(
        index.property_graph_store,
        include_text=True,
        embed_model=Settings.embed_model
    )

    retriever = index.as_retriever(
        sub_retrievers=[
            llm_synonym,
            vector_context,
        ]
        , include_text=True
    )
    nodes = retriever.retrieve(query)
    texts = [clean_text(node.text) for node in nodes]
    concatenated_text = "\n".join(filter(bool, texts))  # 过滤掉空字符串
    return concatenated_text


def clean_text(text):
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # 检查是否为三元组格式
        if '->' in line:
            # 处理三元组，移除 triplet_source_id
            pattern = r'\s*\({\'triplet_source_id\':\s*\'[^\']*\'}\)\s*'
            cleaned_line = re.sub(pattern, '', line).strip()
            cleaned_lines.append(cleaned_line)
        else:
            # 保留非三元组的事实描述
            cleaned_lines.append(line.strip())

    return '\n'.join(cleaned_lines)


if __name__ == "__main__":
    # Example usage
    messages = [
        {
            "role": "user",
            "content": "我最近在研究Cyberlife的功能，尤其是长时记忆和情感理解的部分。你觉得如何更好地整合这些功能？"
        },
        {
            "role": "assistant",
            "content": "这是一个很有趣的挑战！你可以考虑将长时记忆与用户的情感状态相关联，这样当用户在未来遇到相似的情境时，系统可以提供更加个性化的反馈和建议。"
        },
        {
            "role": "user",
            "content": "在设计Cyberlife时，我是否应该优先考虑硬件的扩展性？"
        },
        {
            "role": "assistant",
            "content": "硬件扩展性确实很重要，但它应该与软件功能的发展同步进行。考虑到未来的用户需求，设计时最好保持一定的灵活性，以便能够适应不同的使用场景和硬件更新。"
        },
        {
            "role": "user",
            "content": "今天早上我看到了一篇关于人工智能伦理的文章，提到AI可能会引发的社会挑战。你怎么看？"
        },
        {
            "role": "assistant",
            "content": "AI伦理确实是一个值得关注的重要议题。随着技术的进步，我们需要在开发AI时保持谨慎，确保它们能够负责任地运作，同时不会对社会产生负面影响。与政策制定者和伦理学家合作，建立健全的监管框架，也是非常关键的一步。"
        },
        {
            "role": "user",
            "content": "你觉得伴奂这个名字适合用来形容Cyberlife吗？"
        },
        {
            "role": "assistant",
            "content": "我觉得伴奂这个名字有很强的文化底蕴和意象表达，它传达了陪伴与照耀的概念，非常契合Cyberlife作为智能知己的定位。如果你希望产品具有深厚的文化属性，这个名字是个不错的选择。"
        },
        {
            "role": "user",
            "content": "能帮我找一些与唐代文化相关的资料吗？"
        },
        {
            "role": "assistant",
            "content": "当然可以！唐代是中国历史上的一个辉煌时期，文化艺术成就卓著。我可以为你整理一些关于唐代诗歌、绘画、建筑等方面的资料，方便你进行更深入的研究。"
        },
        {
            "role": "user",
            "content": "昨天和阮亿康打麻将去了，很爽"
        }
    ]

    # graphlize_messages(messages)

    # Example of retrieving information
    query = "阮亿康是谁"
    result = retrieve(query)
    print(result)

    # query_engine = index.as_query_engine(include_text=True)

    # response = query_engine.query(query)

    # print(str(response))
