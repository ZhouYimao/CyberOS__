import html
from unittest import result
import requests
import json
import re
import subprocess
import os
from Google import Google_search
from Reddit import Reddit_search
from Arxiv import Arxiv_search
from Github import Github_search
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader


def load_html(url: str):
    html_loader = WebBaseLoader(url)
    html_data = html_loader.load()
    
    return html_data


def load_pdf(url: str):
    pdf_loader = PyPDFLoader(url,extract_images=True)
    pages = pdf_loader.load_and_split()
    return pages

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

def reddit_part(query: str,result_num: int):
    reddit_results = []
    reddit_results = Reddit_search(query,result_num)
    extracted_results = []
    print("reddit_in")
    #提取每个结果的 url、snippet 和 name
    for result in reddit_results:
        extracted_info = {
            "source": "Reddit",
            "name": result.get("name", "No title"),  
            "url": result.get("url", "No URL"),     
            "snippet": result.get("snippet", "No snippet"),  
            "loader":"No loader"
        }
        if extracted_info['url']!= "No URL":
            extracted_info['loader'] = load_html(extracted_info['url'])
        extracted_results.append(extracted_info)     
    return extracted_results

def arxiv_part(query: str,result_num: int):
    arxiv_results = []
    arxiv_results = Arxiv_search(query,result_num)
    extracted_results = []
    print("arxiv_in")
    #提取每个结果的 url、snippet 和 name
    for result in arxiv_results:
        extracted_info = {
            "source": "Arxiv",
            "name": result.get("name", "No title"), 
            "url": result.get("url", "No URL"),
            'pdf_url': result.get('pdf_url',"No pdf_URL"),      
            "snippet": result.get("snippet", "No snippet"),
            "loader":"No loader"
        }
        print(extracted_info.get('snippet'))

        if extracted_info['pdf_url']!= "No URL":
            extracted_info['loader'] = load_pdf(extracted_info['pdf_url'])
        extracted_results.append(extracted_info)     
    return extracted_results
    
def github_part(query: str,result_num: int):
    github_results = []
    github_results = Github_search(query,result_num)
    extracted_results = []
    print("github in")
    #提取每个结果的 url、snippet 和 name
    for result in github_results:
        extracted_info = {
            "source": "Github",
            "name": result.get("name", "No title"), 
            "url": result.get("url", "No URL"),      
            "snippet": result.get("snippet", "No snippet"),
            "loader":"No loader"
        }
        extracted_results.append(extracted_info)     
    return extracted_results

@tool
def search(init_query: str) ->list:
    """总结：
        当你在本地知识库查询后,仍无法合理地回答用户提出的问题时,需要调用search,联网搜索,获取snippet、url以及url对应的文本内容等重要信息，帮助你回答问题。

    参数:
        init_query: 用户提出的初始问题

    返回值:
        list: 一个包含'url'、'name'、'snippet'以及'id'(搜索结果的编号)4项的字典列表即all_search_results。
        其中snippet是搜索结果的关键信息,对你回答用户的问题非常有帮助;url可能用于further_search。
    """
    query_list = []#此处改写query得到一个query_list
    
    
    result_num = 8
    all_search_results =  [] #存储所有搜索引擎的查询结果
    order = 0
    for query in query_list:
        #调Google,提取每个结果的 url、snippet、name
        order+=1
        all_search_results.extend(google_part(query,result_num,order))  
    return all_search_results
    
def further_search(search_results: list) ->list: 
    """总结:
        当你从snippet信息中无法做出精准的、有效的的回答,这时候你需要进行further_search,获取url列表中网页的更详细的信息,从而帮助你更好的回答query。

    参数:
        url_list (list): 一个包含'url'、'name'、'snippet'以及'id'(搜索结果的编号)4项的字典列表即all_search_results。由search函数返回值传入

    返回值:
        list: 返回一个以查询url后得到网页具体内容为元素的列表
    """
    
    basic_prompt=f"""
    你是由Cyberlife构建的大型语言AI助手。你将获得一个用户问题，并请为这个问题写出干净、简洁、准确的回答。
    你将获得一组与问题相关的上下文，每个上下问都以引用编号开始，如[[citation:x]]，其中x是一个数字。如果适用的话，请使用上下文并在每个句子末尾引用上下文。
    你的回答必须是正确的、准确的，并且以专家的身份用公正和专业的语调书写。请限制在1024个tokens以内。
    不要提供与问题无关的任何信息，不要重复。如果给定的上下文没有提供足够的信息，
    
    You are a large language AI assistant built. You are given a user question, and please write clean, concise and accurate answer to the question. You will be given a set of related contexts to the question, each starting with a reference number like [[citation:x]], where x is a number. Please use the context and cite the context at the end of each sentence if applicable.

    Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. Say "information is missing on" followed by the related topic, if the given context do not provide sufficient information.

    Please cite the contexts with the reference numbers, in the format [citation:x]. If a sentence comes from multiple contexts, please list all applicable citations, like [citation:3][citation:5]. Other than code and specific names and citations, your answer must be written in the same language as the question.

    Here are the set of contexts:

    {context}

    Remember, don't blindly repeat the contexts verbatim. And here is the user question:
    {query_list[0]}
    """
    llm_response=llm.invoke(basic_prompt)
    print(llm_response)
    
    
    jina_url_loader = []
    for init_url in url_list:
        jina_url = 'https://r.jina.ai/'+init_url
        curl_jina = f'curl {jina_url}'
        jina_result = subprocess.run(curl_jina,shell=True,capture_output=True,text=True)
        jina_output = jina_result.stdout
        jina_url_loader.append(jina_output)
    return jina_url_loader

def further_search
    chain（15个api，进一步搜索的id）
    
    return id 
     
        
