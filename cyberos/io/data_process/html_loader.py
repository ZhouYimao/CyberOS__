import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

# 真正的代码
from cyberos.tool.skills.search.url_parse import parse
import asyncio
def html_loader(url: str):
    urls = [url]
    results = asyncio.run(parse(urls))
    result = results[0]['page_content']
    return result
