"""
单元加载多文件、网址、图片、语音输入
文档类(pdf,docx,doc)
.md
.txt
图片
音频
视频
网页
bilibili，youtube
.eml
"""
from typing import Dict
from fileData import is_url,get_fileData_from_url
from pdf_loader import pdf_loader_from_fileData
save_dir = './data'

def url_loader(url_input:str):
    file_data = get_fileData_from_url(url_input)
    if file_data['has_extension'] == None: 
        #说明还不能处理这种url
        print("Unknown Type!")
    else :
        if file_data['file_extension'] == 'pdf' :
            pdf_data = pdf_loader_from_fileData(file_data)
            print(pdf_data['metadata'])
            print(pdf_data['text'])
        else :
            print('Other Type!')
def main():
    file_input = 'https://arxiv.org/pdf/2312.04547'
    if is_url(file_input):
        print("Url_file")
        # url单独处理
        url_loader(file_input)
    else :
        # 本地文件方便处理
        print('Local_file')

if __name__ == "__main__":
    main()