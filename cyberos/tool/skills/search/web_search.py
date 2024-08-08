from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from Google import Google_search

INFERENCE_SERVER_URL = "http://127.0.0.1:8011/v1"

# Initialize the ChatOpenAI model
model = ChatOpenAI(
    model="qwen2-instruct",
    openai_api_key="EMPTY",
    openai_api_base=INFERENCE_SERVER_URL,
    temperature=0.7,
)

# Define the filtering instructions
filter_instructions = """
你是一个非常擅长判断的大语言模型。你会接收到一个问题和一组搜索结果，每个结果包含一个 snippet。你的任务是判断哪些搜索结果需要进一步读取网页全文，并返回这些结果的序号List[int]作为参数。

筛选标准（只作为示例，可自行判断）：
1. 如果 snippet 信息不足以回答问题，需要读取全文。
2. 如果 snippet 内容与问题直接相关但不完整，需要读取全文。
3. 如果 snippet 内容有重要但未详细展开的信息，需要读取全文。
...
注：上下文有限制，尽量不要返回超过5个

请严格按照以下格式返回结果（List[int]），否则无法解析参数：
[序号1, 序号2, 序号3, ...]
"""  
query = ''
# Example content for human message, this can be modified as needed
human_message_content = f"""
Query = "{query}"
search_results = [
    1:"提高机器学习模型的准确性有多种方法，例如...",
   2: "数据预处理是提高模型准确性的关键步骤之一。",
    3:"选择合适的模型和参数调整能够显著提升模型表现。",
    4. "模型集成是另一种有效的方法，通过结合多个模型的预测结果来提高准确性。"
    
]
"""

# Create the message sequence
messages = [
    SystemMessage(content=filter_instructions),
    HumanMessage(content=human_message_content),
]

# Initialize the output parser
parser = StrOutputParser()

# Create the processing chain
chain = model | parser

# Invoke the chain with the messages
result = chain.invoke(messages)

# Print the result
print(result)

def google_part(query: str,result_num: int,order: int):
    google_results = []  # 存储提取后的每个查询结果
    google_results = Google_search(query,result_num)
    extracted_results = []
    print("google_in")
    #提取每个结果的 url、snippet 和 name
    for result in google_results:
        extracted_info = {
            "name": result.get("name", "No title"),  
            "url": result.get("url", "No URL"),     
            "snippet": result.get("snippet", "No snippet"),
            "id": order
        }
        extracted_results.append(extracted_info)     
    return extracted_results
    
    
# @tool
# def search(query: str) -> str:
#     """
#     联网搜索，传入的参数query是你认为需要联网查询的问题，
#     返回的结果一个str，包含snippet摘要和把网页详细内容RAG之后的回答
#     """
#     query_list = generate_queries(init_query)  # 生成子查询列表
#     all_search_results = []

#     for query in query_list:
#         results = call_search_api(query)  # 调用搜索API，获取结果
#         all_search_results.extend(results)

#     return all_search_results

# def further_search(search_results: list) -> list:
#     """
#     总结:
#         根据初步搜索结果进一步获取详细信息。
#         该工具用于当初步搜索结果的 snippet 信息不足以做出精准回答时，进一步获取详细信息以帮助更好地回答用户的问题。

#     参数:
#         search_results: 初步搜索结果列表，包含 'url', 'name', 'snippet', 以及 'id'

#     返回值:
#         list: 包含进一步搜索得到的网页内容的列表
#     """
#     detailed_results = []
"""
你是一个非常擅长判断的大语言模型。你会接收到一个问题和一组搜索结果，每个结果包含一个 snippet。你的任务是判断哪些搜索结果需要进一步读取网页全文，并返回这些结果的序号List[int]作为参数。

筛选标准（只作为示例，可自行判断）：
1. 如果 snippet 信息不足以回答问题，需要读取全文。
2. 如果 snippet 内容与问题直接相关但不完整，需要读取全文。
3. 如果 snippet 内容有重要但未详细展开的信息，需要读取全文。
...
注：上下文有限制，尽量不要返回超过5个

请严格按照以下格式返回结果（List[int]），否则无法解析参数：
[序号1, 序号2, 序号3, ...]
"""  
# 问题：{query}
# 搜索结果：
# 1. {snippet1}
# 2. {snippet2}
# ...

# for result in search_results:
#         detailed_content = fetch_url_content(result['url'])  # 获取URL内容
#         detailed_results.append(detailed_content)

#     return detailed_results

# def generate_final_answer(contexts: list, query: str) -> str:
#     """
#     生成最终的回答，基于提供的上下文和查询。

#     参数:
#         contexts: 上下文列表，每个上下文以引用编号开头
#         query: 用户的初始查询

#     返回值:
#         str: 最终生成的回答
#     """
#     prompt = f"""
#     你是由Cyberlife构建的大型语言AI助手。你将获得一个用户问题，并请为这个问题写出干净、简洁、准确的回答。
#     你将获得一组与问题相关的上下文，每个上下文都以引用编号开始，如[[citation:x]]，其中x是一个数字。如果适用的话，请使用上下文并在每个句子末尾引用上下文。
#     你的回答必须是正确的、准确的，并且以专家的身份用公正和专业的语调书写。请限制在1024个tokens以内。
#     不要提供与问题无关的任何信息，不要重复。如果给定的上下文没有提供足够的信息，说明信息不足。

#     这里是提供的上下文：

#     {contexts}

#     这里是用户的问题：
#     {query}
#     """
#     final_answer = call_llm(prompt)  # 调用大型语言模型生成回答
#     return final_answer

# # Helper functions
# def generate_queries(init_query: str) -> list:
#     """
#     根据初始查询生成多个子查询。
#     """
#     # 示例生成逻辑
#     return [init_query, init_query + " example", init_query + " details"]

# def call_search_api(query: str) -> list:
#     """
#     调用搜索API，返回结果列表。
#     """
#     # 示例API调用
#     return [{"url": "example.com", "name": "Example", "snippet": "Example snippet", "id": 1}]

# def fetch_url_content(url: str) -> str:
#     """
#     获取指定URL的内容。
#     """
#     # 示例获取逻辑
#     return "Detailed content from example.com"

# def call_llm(prompt: str) -> str:
#     """
#     调用大型语言模型，返回生成的回答。
#     """
#     # 示例调用逻辑
#     return "Generated answer based on provided contexts."

# # 主函数示例调用
# if __name__ == "__main__":
#     init_query = "用户的初始问题"
#     search_results = search(init_query)
#     detailed_results = further_search(search_results)
#     final_answer = generate_final_answer(detailed_results, init_query)
#     print(final_answer)
    
    

