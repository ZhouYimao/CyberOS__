import os
import mimetypes
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_doc
from unstructured.partition.docx import partition_docx
from unstructured.partition.xlsx import partition_xlsx
from unstructured.partition.csv import partition_csv
from unstructured.partition.html import partition_html
from unstructured.partition.text import partition_text
from unstructured.partition.image import partition_image
from unstructured.partition.md import partition_md
from unstructured.partition.ppt import partition_ppt
from unstructured.partition.pptx import partition_pptx
from docx_loader import docx_loader
from pdf_loader import pdf_loader
from html_loader import html_loader
from cleaning import clean_text
from url_tool import is_url,get_ext_from_url,check_url



# 根据文件扩展名选择分割函数的字典
partition_functions = {
    '.html': html_loader,
    '.xlsx': partition_xlsx,
    '.csv': partition_csv,
    '.txt': partition_text,
    # 为图像文件添加更多扩展名
    '.png': partition_image,
    '.jpg': partition_image,
    '.jpeg': partition_image,
    '.md': partition_md,
    '.ppt': partition_ppt,
    '.pptx': partition_pptx,
}

# complete_file就是url或者本地文件的完整路径
def local_loader_cleaning(complete_file: str):
    # is_file_url为True表示是url，反之是本地文件
    is_file_url = is_url(complete_file)
    # 无论是url还是本地文件，都获取后缀名
    if is_file_url:
        url_exist,code = check_url(complete_file) #是url还要检查url是否有效
        if url_exist:
            ext = get_ext_from_url(complete_file)
        else :
            print(code)
            return ''
    else :
        if os.path.isfile(complete_file):
            ext = os.path.splitext(complete_file)[1].lower()
        else :
            print("Error,File Not Exists!")
            return ''  
    partition_func = partition_functions.get(ext)
    cleaned_text = ''

    if partition_func:
        try:
            # 根据输入类型调用不同的分割函数
            if is_file_url:
                # 主要就是针对.html
                elements = partition_func(url = complete_file)
            else:
                elements = partition_func(filename = complete_file)
            print(ext)
            for element in elements:
                clean_element_text = element.text
                cleaned_text += clean_element_text + ' '
            cleaned_text = clean_text(cleaned_text)
        except Exception as e:
            print(f"Error partitioning {complete_file}: {e}")
    elif ext == '.docx':
        cleaned_text = docx_loader(complete_file)
    elif ext == '.pdf':
        cleaned_text = pdf_loader(complete_file)
    else:
        print(f"No partition function found for file extension: {ext}")
    return cleaned_text

def loader(file_input: str):
    return local_loader_cleaning(file_input)
    
if __name__ == "__main__":
    file_input = 'https://open.bigmodel.cn/'
    cleaned_text = loader(file_input)
    print(cleaned_text)