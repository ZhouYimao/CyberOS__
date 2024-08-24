from langchain_community.document_loaders import PyMuPDFLoader
import os
import fitz
import requests
from typing import Dict
from urllib.parse import urlparse

save_dir = './data'
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

    file_data = {
        'url': url,
        'file_name':file_name,
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
            file_data = {
                'url': url,
                'file_name':file_name,
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


def extract_images_from_pdf(doc, pdf_name, pdf_path):
    
    # 创建images文件夹
    images_dir = os.path.join(pdf_path,'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    # 遍历文档中的所有页面
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)  # 加载页面
        # 获取页面上所有图像的信息
        image_list = page.get_images()
        for img_index, img_info in enumerate(image_list, start=1):
            # img_info是一个包含图像信息的字典
            xref = img_info[0]  # xref是图像在PDF中的引用
            base_image = fitz.Pixmap(doc, xref)  # 使用xref创建图像对象
            # 构造图像文件名并保存图像到指定文件夹
            image_filename = f"page_{page_number + 1}_image_{img_index}.png"
            image_save_path = os.path.join(images_dir, image_filename)
            base_image.save(image_save_path)
            print(f"Image saved as: {image_save_path}")

def extract_MetadataAndText_from_pdf(doc):
    metadata = doc.metadata
    # 初始化一个空字符串来存储整个文档的文本
    full_text = ""
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        page_text = page.get_text()
        full_text += page_text + "\n\n"  # 添加换行符以分隔不同页面的文本
    
    return metadata,full_text
    
"""
pdf_name如dt
pdf_path如./data/dt
dt文件在./data/dt
完整路径是./data/dt/dt即在complete_pdf_path中
"""
def pdf_process(pdf_name: str, pdf_path: str, extract_images: bool):
    complete_filename = pdf_name + '.pdf'
    complete_pdf_path = os.path.join(pdf_path,complete_filename)
    doc = fitz.open(complete_pdf_path)
    metadata, text = extract_MetadataAndText_from_pdf(doc)
    # 检查是否需要提取图像
    if extract_images:
        extract_images_from_pdf(doc,pdf_name,pdf_path)
    doc.close()
    pdf_data = {
        'metadata': metadata,
        "text": text
    }
    return pdf_data


def download_pdf_from_fileData(file_data: Dict):
    # 在save_dir下创建与文件名同名的文件夹
    folder_path = os.path.join(save_dir,file_data['file_name'])
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # 构建完整的保存路径，包括文件夹和原始URL中的文件名
    complete_filename = file_data['file_name'] + '.' + file_data['file_extension']
    save_path = os.path.join(folder_path, complete_filename)
    with open(save_path, 'wb') as file:
        file.write(file_data['content'])
    return folder_path

def pdf_loader(file_data: Dict):
    # pdf_path是保存在本地的所属目录位置
    pdf_path = download_pdf_from_fileData(file_data)
    pdf_name = file_data['file_name']
    # 对本地pdf进行处理
    extract_images = False
    pdf_data = pdf_process(pdf_name, pdf_path, extract_images)


def url_loader(url_input:str):
    file_data = get_fileData_from_url(url_input)
    if file_data['has_extension'] == None: 
        #说明还不能处理这种url
        print("Unknown Type!")
    else :
        if file_data['file_extension'] == 'pdf' :
            pdf_loader(file_data)
        else :
            print('Other Type!')

def main():
    file_input = 'https://arxiv.org/pdf/2103.15348.pdf'
    if is_url(file_input):
        print("Url_file")
        # url单独处理
        url_loader(file_input)
    else :
        # 本地文件方便处理
        print('Local_file')

if __name__ == "__main__":
    main()