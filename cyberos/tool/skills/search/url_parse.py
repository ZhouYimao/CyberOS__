import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, urljoin
from typing import List, Dict
import re
'''
外部调用方法：
    from url_parse import url_parse
    results = asyncio.run(url_parse(your_url))


    传入一个ur1,读取url中的page_content以及子链接   
    返回{'origin_url':xxx, 'page content':xxx,'link':[{'url':xxx,description':xxx}1}
'''

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

    # 从解析结果中提取协议和网络位置
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc

    # 将协议和网络位置组合成包含协议的完整域名
    domain_with_scheme = urlunparse((scheme, netloc, '', '', '', ''))
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


async def fetch_page(init_url: str):
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=1)
    # 使用无头模式启动 Chrome
    options = Options()
    options.add_argument('--headless')  # 启用无头模式
    
    future = loop.run_in_executor(executor, lambda: browse(init_url, options))
    return await future

def browse(url:str, options) :
    driver = webdriver.Chrome(options=options)
    # 获取init_url中的信息
    driver.get(url)
    driver.implicitly_wait(10)  # 等待最多10秒

    html = driver.page_source
    init_soup = BeautifulSoup(html, 'html.parser')
    
    # 清洗文本
    paragraphs = init_soup.find_all('p')
    # 初始化一个空字符串用于存储清洗后的文本
    clean_text_content = ''
    # 遍历所有的<p>标签
    for para in paragraphs:
        # 提取文本并去除前后空白字符
        text = para.get_text(strip=True)
        # 去除文本中的大段空格
        cleaned_text = re.sub(r'\s+', ' ', text)
        # 将清洗后的文本添加到结果字符串中
        clean_text_content += cleaned_text
    
    '''
    text_content = init_soup.get_text(separator=' ', strip=True)
    clean_text_content = ' '.join(text_content.split())
    '''
    
    # 提取所有链接的文本描述
    links_and_descriptions = []
    links = init_soup.find_all('a', href=True)
    id_num = 0
    for link in links:
        href = link.get('href')
        if href.startswith('#'):
            continue
        piece_url = url_process(href,url)
        piece_description = link.get_text(strip=True)
        id_num += 1
        link_and_description = {
            'id': id_num,
            'url': piece_url,
            'description': piece_description
        }
        links_and_descriptions.append(link_and_description)
    
    all_message = {'origin_url':url,'page_content':clean_text_content}
    all_message['link'] = links_and_descriptions
    driver.quit()  # 确保退出浏览器
    return all_message

async def parse(urls: list):
    tasks = [fetch_page(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

if __name__ == "__main__":
    urls = [
        'https://www.facebook.com',
        #'https://langchain-ai.github.io/langgraph/tutorials/#rag',
        #'http://www.manwei.wang/contents/View/1796.html',
        #'https://www.sohu.com/a/254277297_100228214',
        #'https://www.sohu.com/a/675526781_121687416'
    ]
    results = asyncio.run(parse(urls))
    for result in results:
        print(result['page_content'])

