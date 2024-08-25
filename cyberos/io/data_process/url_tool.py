import os
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout, RequestException

from urllib.parse import urlparse
extension_list = ['.pdf','.html','.htm','.jpeg','.jpg','.png','.mp3','.mp4']

def check_url(url):
    try:
        response = requests.head(url, timeout=5)  # 发送HEAD请求，获取响应头
        response.raise_for_status()  # 如果响应状态码不是 200，则引发HTTPError异常
        return True,200
    except ConnectionError:
        return False,f"Failed to connect to URL: {url}"
    except HTTPError as http_err:
        return False,f"HTTP error occurred: {http_err}"
    except Timeout:
        return False,f"Request to URL timed out: {url}"
    except RequestException as req_err:
        return False,f"An error occurred: {req_err}"

def is_url(url: str):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
def get_ext_from_url(url: str):
    parsed_url = urlparse(url)
    basename = os.path.basename(parsed_url.path)
    _, url_extension = os.path.splitext(basename)
    if url_extension in extension_list:
        return url_extension
    else :
        return get_url_content_type(url)

# 当只通过urlname无法判断文件类型时调用（说明此时没有显式的.pdf等后缀）
def get_url_content_type(url):
    try:
        response = requests.get(url)
        # 检查请求是否成功
        response.raise_for_status()
        # 获取Content-Type字段
        content_type = response.headers.get('Content-Type', 'Unknown')

        parts = content_type.split(';')
        base_type = parts[0].strip()

        # 定义Content-Type到文件后缀名的映射字典
        content_type_to_extension = {
            'application/pdf': '.pdf',
            'text/html': '.html',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'video/mp4': '.mp4',
            'audio/mp3': '.mp3',
            # 可以根据需要添加更多的MIME类型和对应的文件后缀
        }
        # 根据Content-Type得到后缀
        file_extension = content_type_to_extension.get(base_type,'Unknown')
        if file_extension=='Unknown':
            print(f"An error occurred: Type of url Unknown!")
            return "Unknown"
        else:
            return file_extension
    except requests.RequestException as e:
        # 如果请求出现问题，打印错误信息
        print(f"An error occurred: {e}")
        return None
    
def main():
    file_input = 'https://arxiv.org/pdsf/2103.1538'
    print(get_ext_from_url(file_input))
    
if __name__ == "__main__":
    main()