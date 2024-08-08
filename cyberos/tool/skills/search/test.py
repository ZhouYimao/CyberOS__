from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import ast
from Google import Google_search
import subprocess

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

# Function to create human message content
def create_human_message_content(query: str, search_results: list) -> str:
    formatted_results = ",\n".join([f'{result["id"]}: "name: {result["name"]}, snippet: {result["snippet"]}"' for result in search_results])
    return f'Query = "{query}"\nsearch_results = [\n{formatted_results}\n]'

# Function to get google search results
def google_part(query: str, result_num: int):
    google_results = Google_search(query, result_num)
    extracted_results = []
    for order, result in enumerate(google_results, start=1):
        extracted_info = {
            "name": result.get("name", "No title"),
            "url": result.get("url", "No URL"),
            "snippet": result.get("snippet", "No snippet"),
            "id": order
        }
        extracted_results.append(extracted_info)
    return extracted_results

# Function to generate three related questions from the initial query
def generate_related_questions(query: str):
    related_questions = []
    related_questions.append(f"{query} 的主要挑战是什么？")
    related_questions.append(f"{query} 的最新研究进展有哪些？")
    related_questions.append(f"如何应用 {query} 在实际项目中？")
    return related_questions

# Function to process search results and determine which need further reading
def process_search_results(query: str, search_results: list):
    related_questions = generate_related_questions(query)
    all_results = []
    for related_query in related_questions:
        human_message_content = create_human_message_content(related_query, search_results)
        messages = [
            SystemMessage(content=filter_instructions),
            HumanMessage(content=human_message_content),
        ]
        parser = StrOutputParser()
        chain = model | parser
        result = chain.invoke(messages)
        print(result)
        all_results.extend(ast.literal_eval(result))
    return list(set(all_results))  # 去重并返回所有需要进一步阅读的结果

# Function to load content from URLs
def load_url_contents(search_results: list, ids: list):
    url_list = [result['url'] for result in search_results if result['id'] in ids]
    jina_url_loader = []
    for init_url in url_list:
        jina_url = 'https://r.jina.ai/' + init_url
        curl_jina = f'curl {jina_url}'
        jina_result = subprocess.run(curl_jina, shell=True, capture_output=True, text=True)
        jina_output = jina_result.stdout
        jina_url_loader.append(jina_output)
    return jina_url_loader

# Main function
def main(query: str, result_num: int):
    search_results = google_part(query, result_num)
    filtered_ids = process_search_results(query, search_results)
    detailed_contents = load_url_contents(search_results, filtered_ids)
    print(detailed_contents)

# Example call
if __name__ == "__main__":
    init_query = "提高机器学习模型的准确性"
    result_num = 5  # Number of search results to fetch
    main(init_query, result_num)