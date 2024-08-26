import requests
import re
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urlunparse, urljoin
from typing import List, Dict
from cleaning import clean_text
from .browse_parse import browse_parse

def pre_process(url:str)->str:
    '''
    删除url中的#定位符
    '''
    hash_index = url.find('#')
    if hash_index != -1:
        # 删除#及其后面的所有字符
        url = url[:hash_index]
    # 如果url末尾没有/,则补充一个
    url = url if url.endswith('/') else url + '/'
    return url

def get_domain(url: str)->str:
    '''
    提取给定url的域名
    '''
    # 使用urlparse函数解析URL
    parsed_url = urlparse(url)


    # 将协议和网络位置组合成包含协议的完整域名
    domain_with_scheme = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
    return domain_with_scheme


def url_process(piece_url:str,init_url:str) ->str :
    '''
    init_url是用户最初给的链接
    piece_url是母链接下的子链接
    '''
    # 对init_url预处理
    init_url = pre_process(init_url)
    # 解析url
    parsed_url = urlparse(piece_url)

    # 如果URL包含协议和网络位置，则认为是绝对路径,且可直接访问,不做处理
    if bool(parsed_url.scheme) and bool(parsed_url.netloc):
        return piece_url
    # 如果URL以'/'开头且没有协议和网络位置，也认为是绝对路径,但需要进一步处理
    elif piece_url.startswith('/') and not bool(parsed_url.scheme) and not bool(parsed_url.netloc):
        # 获取域名
        domain_url = get_domain(init_url)
        return domain_url+piece_url
    # 不然认为是相对路径,返回拼接后的路径
    else:
        return urljoin(init_url,piece_url)
    

async def fetch_page(url: str, session: aiohttp.ClientSession):
    async with session.get(url) as response:
        if response.status == 200:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=' ', strip=True)
            text = clean_text(text)

            links_and_descriptions = []
            links = soup.find_all('a', href=True)
            id_num = 0
            for link in links:
                href = link.get('href')
                if href.startswith('#'):
                    continue
                piece_url = url_process(href, url)
                piece_description = link.get_text(strip=True)
                id_num += 1
                link_and_description = {
                    'id': id_num,
                    'url': piece_url,
                    'description': piece_description
                }
                links_and_descriptions.append(link_and_description)

            all_message = {'origin_url': url, 'page_content': text, 'link': links_and_descriptions}
            return all_message
        else:
            return {'origin_url': url, 'error': f"Failed to retrieve content, status code: {response.status}"}

async def parse(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(url, session) for url in urls]
        results = await asyncio.gather(*tasks)
         # 提取需要调用 browse_parse 的 URL 列表
        urls_to_browse = [result['origin_url'] for result in results if 'link' not in result or not result['link']]
        if urls_to_browse:
            browse_results = await browse_parse(urls_to_browse)
            # 创建一个字典，方便根据 origin_url 查找 browse_results 中的对应元素
            browse_results_dict = {res['origin_url']: res for res in browse_results}
            
            for i, result in enumerate(results):
                if result['origin_url'] in urls_to_browse:
                    # 用 browse_results_dict 中对应的元素替换 results 中的元素
                    results[i] = browse_results_dict[result['origin_url']]
                    
                
        return results  # 包含所有结果的列表


if __name__ == "__main__":
    # 需要解析的网页URL
    urls = [
        'https://zh.wikihow.com/%E6%89%93%E5%BC%80EML%E6%96%87%E4%BB%B6',
        'https://langchain-ai.github.io/langgraph/tutorials/#rag',
        'http://www.manwei.wang/contents/View/1796.html',
        'https://www.sohu.com/a/254277297_100228214',
        'https://www.sohu.com/a/675526781_121687416',
        #'https://www.apple.com/',
        'https://open.bigmodel.cn/',
        #'https://developer.apple.com/documentation/swiftui/'
    ]
    results = asyncio.run(parse(urls))
    for result in results:
        print(result['page_content'])
    
