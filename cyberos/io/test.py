from langchain_community.document_loaders import PyMuPDFLoader
import os
import fitz
import requests
import re 
from typing import Dict
from urllib.parse import urlparse

extension_list = ['pdf','html','htm','jpeg','jpg','png','gif','mp3','mp4','doc','docx']

def is_url(url: str):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_fileData_from_urlname(url: str):
    parsed_url = urlparse(url)
    basename = os.path.basename(parsed_url.path)
    file_name, url_extension = os.path.splitext(basename)
    url_extension = url_extension.lstrip('.')
    has_extension = False
    if url_extension in extension_list:
        has_extension = True
    complete_fileName = file_name + '.' + url_extension
    file_data = {
        'url': url,
        'file_name':complete_fileName,
        'file_extension':url_extension,
        'has_extension':has_extension
    }
    return file_data

# 当只通过urlname无法判断文件类型时调用（说明此时没有显式的.pdf等后缀）
def get_url_content_type(url):
    try:
        response = requests.get(url)

        # 检查请求是否成功
        response.raise_for_status()

        content = response.content

        # 获取Content-Type字段
        content_type = response.headers.get('Content-Type', 'Unknown')

        parts = content_type.split(';')
        base_type = parts[0].strip()

        # 定义Content-Type到文件后缀名的映射字典
        content_type_to_extension = {
            'application/pdf': 'pdf',
            'text/html': 'html',
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'video/mp4': 'mp4',
            'audio/mp3': 'mp3',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx'
            # 可以根据需要添加更多的MIME类型和对应的文件后缀
        }
        # 根据Content-Type得到后缀
        file_extension = content_type_to_extension.get(base_type,'Unknown')
        if file_extension=='Unknown':
            print(f"An error occurred: Type of url Unknown!")
            file_data = {
                'url':url,
                'file_name':None,
                'file_extension':None,
                'content':None,
                'has_extension':None
            }
            return file_data
        else:
            parsed_url = urlparse(url)
            parsed_url_path = parsed_url.path.rstrip('/')
            file_name = os.path.basename(parsed_url_path)
            complete_fileName = file_name + '.' + file_extension
            file_data = {
                'url': url,
                'file_name':complete_fileName,
                'file_extension':file_extension,
                'content':content,
                'has_extension':False
            }
            return file_data
    except requests.RequestException as e:
        # 如果请求出现问题，打印错误信息
        print(f"An error occurred: {e}")
        return None

def get_fileData_from_url(url: str):
    file_data = get_fileData_from_urlname(url)
    if file_data['has_extension']:
        print('Already Success!')
        try:
            response = requests.get(url)
            # 检查请求是否成功
            response.raise_for_status()
            content = response.content
            file_data['content'] = content
        except requests.RequestException as e:
            # 如果请求出现问题，打印错误信息
            print(f"An error occurred: {e}")
            return None
    else :
        print('Further Try!')
        file_data = get_url_content_type(url)
    return file_data

url = 'https://arxiv.org/pdf/2312.04547'
file_data = get_fileData_from_url(url)
if file_data['has_extension'] == None:
    print("cao")
else :
    print(file_data['file_name'])

#file_data = get_url_content_type(url)
#print(file_data)
#file_name = get_filename_from_file_data(file_data)
#print(file_name)