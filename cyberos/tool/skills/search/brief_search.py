from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import ChatPromptTemplate
import bs4
import requests
from .url_parse import parse
import ast
from tenacity import retry_all
from .Google import Google_search
import subprocess
import asyncio
from .config.prompts import (
    query_translations,
    detailed_answer_prompt,
    select_description_prompt,
    snippet_answer_prompt,
    judge_prompt,
    filter_instructions
)

#原始问题 -> 3个子问题 -> 搜索 -> 判断 -> 加载网页内容 -> 根据问题总结网页内容 -> 结合snippet和网页内容摘要回答原始
# Initialize the ChatOpenAI model
query_model = ChatOpenAI(
    temperature=0.7,
    api_key="671cd8a40b399a97b23df3036898cdc2.GsVP1rLCEGlQm8iX",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4",
    model="glm-4-airx",
)

load_model = ChatOpenAI(
    temperature=0.7,
    api_key="671cd8a40b399a97b23df3036898cdc2.GsVP1rLCEGlQm8iX",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4",
    model="glm-4-flash",
)


def query_translate(original_query: str) :
    query_translations = """
    你需要将原始问题转换为3个可以在Google搜索的内容（也可以是关键词，可以用空格隔开），
    尽量覆盖不同方面。以供后续的搜索引擎获取相关信息。
    三个问题需要用换行符分隔，且不包含序号，例如：
    原始问题：如何在langchain中调用工具？
    生成结果：langchain tool\nlangchain 工具\nlangchain tool doc

    原始问题是：{question}
    """
    prompt_perspectives = ChatPromptTemplate.from_template(query_translations)

    generate_queries = (
        prompt_perspectives
        | query_model
        | StrOutputParser()
        | (lambda x: x.split("\n"))
    )

    related_queries = generate_queries.invoke({'question': original_query})
    return related_queries

# Function to create human message content
def create_human_message_content(query: str, search_results: list) -> str:
    formatted_results = ",\n".join([f'{result["id"]}: "name: {result["name"]}, snippet: {result["snippet"]}"' for result in search_results])
    output = f'Query = "{query}"\nsearch_results = [\n{formatted_results}\n]'
    return output

# Function to get google search results
def google_part(query: str, result_num: int, start_id: int):
    google_results = Google_search(query, result_num)
    extracted_results = []
    for order, result in enumerate(google_results, start=start_id):
        extracted_info = {
            "name": result.get("name", "No title"),
            "url": result.get("url", "No URL"),
            "snippet": result.get("snippet", "No snippet"),
            "id": order
        }
        extracted_results.append(extracted_info)
    return extracted_results


# Function to process search results and determine which need further reading
def process_search_results(query: str, search_results: list):
    human_message_content = create_human_message_content(query, search_results)
    messages = [
        SystemMessage(content=filter_instructions),
        HumanMessage(content=human_message_content),
    ]
    parser = StrOutputParser()
    chain = query_model | parser
    result = chain.invoke(messages)
    return ast.literal_eval(result)

# Function to load content from URLs


def summarize_with_snippet(query: str,search_results: list):
    snippets_contents = ''
    id_num = 0 
    for item in search_results:
        if 'snippet' in item and 'url' in item:
            # 提取snippet和id
            snippet = item['snippet']
            url = item['url']
            id_num += 1
            snippet_piece = f'[{id_num}]({url}):{snippet}'
            snippets_contents += ('\n' + snippet_piece)
    prompt = snippet_answer_prompt + snippets_contents
    answer_chain = load_model | StrOutputParser()
    answer = answer_chain.invoke([SystemMessage(content=prompt), HumanMessage(content=query)])
    return answer
    
'''
def judge_response(query: str, answer: str):
    prefix_answer = f'[answer]:{answer}'
    prompt = judge_prompt + prefix_answer
    judge_chain = query_model | StrOutputParser()
    judeg_result = judge_chain.invoke([SystemMessage(content=prompt), HumanMessage(content=query)])
    return judge_result
'''

# Main function
def get_response(query: str, result_num: int):
    related_queries = query_translate(query)
    all_search_results = []
    current_id = 1

    for sub_query in related_queries:
        search_results = google_part(sub_query, result_num, current_id)
        all_search_results.extend(search_results)
        current_id += result_num
    
    snippet_answer = summarize_with_snippet(query,all_search_results)
    '''
    filtered_ids = process_search_results(query, all_search_results)
    detailed_contents = load_url_contents(all_search_results, filtered_ids)
    print(detailed_contents)
    # Summarize contents and generate answer
    prompt = summarize_and_answer(query, detailed_contents, all_search_results)
    # print(answer)
    '''
    return snippet_answer

'''
def load_href(url_parse_results: list,query: str):
    prompt1_piece = ''
    for result in url_parse_results:
        for url_and_desc in result['link']:
            piece_id = url_and_desc['id']
            piece_desc = url_and_desc['description']
            piece_prompt = f'[{piece_id}]:piece_desc'
            prompt1_piece += (piece_prompt + '\n') 
    print(prompt1_piece)
    prompt1 = select_description_prompt + prompt1_piece
    select_chain = query_model | StrOutputParser()
    select_chain_result = select_chain.invoke([SystemMessage(content=prompt1),HumanMessage(content=query)])
    print(select_chain_result)
    selected_ids = ast.literal_eval(select_chain_result)
    print(selected_ids)
    #selected_urls = [r['url'] for r in result['link'] if r['id'] in selected_ids]
    #selected_results = asyncio.run(url_parse(selected_urls))
    #href_contents = ''
    #for result in selected_results:
    #    href_contents += result['page_content']
    #return href_contents
'''

def detailed_search(query: str, url: str):
    url_list = []
    url_list.append(url)
    url_parse_results = asyncio.run(parse(url_list))
    url_parse_content = url_parse_results[0]['page_content']
    #load_href(url_parse_results,query)
    #href_contents = load_href(url_parse_results)
    prompt2 = detailed_answer_prompt + url_parse_content
    answer_chain = load_model | StrOutputParser()
    answer = answer_chain.invoke([SystemMessage(content=prompt2), HumanMessage(content=query)])
    print(answer)

def search(init_query: str):
    result_num = 3  # Number of search results to fetch
    return get_response(init_query, result_num)
    
    #detailed_url = "https://news.ifeng.com/c/8bfYHKDjnI9"
    #detailed_search(init_query,detailed_url)
    #print(get_response(init_query, result_num))

# Example call
if __name__ == "__main__":
    init_query = "王楚钦在巴黎奥运会男子单打项目表现如何？"
    print(search(init_query))