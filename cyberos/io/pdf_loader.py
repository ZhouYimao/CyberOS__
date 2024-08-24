from langchain_community.document_loaders import PyPDFLoader
import os
import fitz
from typing import Dict
from fileData import is_url,get_fileData_from_url,extension_list
import time

save_dir = './data'


def extract_images_from_pdf(pdf_name, pdf_path, complete_pdf_path):
    doc = fitz.open(complete_pdf_path)

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
    
    doc.close()

def clean_text(content: str):
    # 将换行符替换为一个空格
    cleaned_text = content.replace('\n', ' ') 
    # 去除 <> 标签
    cleaned_text = cleaned_text.replace('<', '').replace('>', '')
    # 去除 "- " 字符串
    cleaned_text = cleaned_text.replace('- ', '')
    return cleaned_text()

def extract_MetadataAndText_from_pdf(pdf_path: str):
    loader = PyPDFLoader(pdf_path, extract_images=True)
    pages = loader.load()
    metadata = pages[0].metadata
    # 初始化一个空字符串来存储整个文档的文本
    full_text = ""
    for page_number in range(len(pages)):
        content = pages[page_number].page_content
        cleaned_text = clean_text(content)
        full_text += (cleaned_text + '\n\n') # 添加换行符以分隔不同页面的文本
    with open('./new.txt', 'w') as file:
        file.write(full_text)
    return metadata,full_text
"""
pdf_name如dt
pdf_path如./data/dt
dt文件在./data/dt
完整路径是./data/dt/dt即在complete_pdf_path中
"""
def pdf_local_process(pdf_name: str, pdf_path: str, extract_images=False):
    complete_filename = pdf_name + '.pdf'
    complete_pdf_path = os.path.join(pdf_path,complete_filename)

    metadata, text = extract_MetadataAndText_from_pdf(complete_pdf_path)

    # 检查是否需要提取图像
    if extract_images:
        extract_images_from_pdf(pdf_name,pdf_path,complete_pdf_path)
    
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

def pdf_loader_from_fileData(file_data: Dict,extract_images=False):
    # pdf_path是保存在本地的所属目录位置
    pdf_path = download_pdf_from_fileData(file_data)
    pdf_name = file_data['file_name']
    # 对本地pdf进行处理
    pdf_data = pdf_local_process(pdf_name, pdf_path, extract_images)
    return pdf_data

# 从相对/绝对路径中提取出文件名和文件类型
def extract_filename_and_extension(relative_path):
    # 将相对路径转换为绝对路径
    absolute_path = os.path.abspath(relative_path)
    
    # 检查路径是否指向一个文件
    if os.path.isfile(absolute_path):
        # 提取文件名（包含后缀）
        filename_with_extension = os.path.basename(absolute_path)
        
        # 提取文件名（不包含后缀）
        filename = os.path.splitext(filename_with_extension)[0]
        
        # 提取文件后缀名
        extension = os.path.splitext(filename_with_extension)[1]
        
    else:
        print(f"提供的路径不是一个文件: {relative_path}")
    return filename,extension

def copy_file(source_path,target_path):
    # 将相对路径转换为绝对路径
    source_absolute_path = os.path.abspath(source_path)

    # 检查源文件是否存在
    if not os.path.isfile(source_absolute_path):
        print(f"源文件不存在: {source_path}")
        return
    
    # 复制文件
    shutil.copy2(source_absolute_path, target_file_path)
    
    print(f"文件已复制到: {target_file_path}")

def pdf_local_to_local(source_path:str,file_name: str):
    # 在save_dir下创建与文件名同名的文件夹
    folder_path = os.path.join(save_dir,file_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    copy_file(,folder_path)

def main():
    pdf_input = ""
    if is_url(pdf_input):
        file_data = get_fileData_from_url(pdf_input)
        pdf_data = pdf_loader_from_fileData(file_data)
        print(pdf_data['metadata'])
    else :
        file_name,file_extension = extract_filename_and_extension(pdf_input)
        pdf_local_to_local(pdf_input,file_name)
        # 在save_dir下创建与文件名同名的文件夹
        folder_path = os.path.join(save_dir,file_data['file_name'])
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # 构建完整的保存路径，包括文件夹和原始URL中的文件名
        complete_filename = file_data['file_name'] + '.' + file_data['file_extension']
        save_path = os.path.join(folder_path, complete_filename)
        with open(save_path, 'wb') as file:
            file.write(file_data['content'])
        pdf_local_process()    
    
if __name__ == "__main__":
    main()
