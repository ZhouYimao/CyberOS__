from cyberos.tool.skills.search.url_parse import parse
import asyncio
def html_loader(url: str):
    urls = [url]
    results = asyncio.run(parse(urls))
    result = results[0]['page_content']
    return result