import markdown
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import re
import requests
from io import BytesIO
import os
from text_utils import clean_text
from img_loader import img_loader
import mistune



def extract_text_from_markdown(file_content: str, uploaded_images: dict):
    # 将Markdown内容转换为HTML
    html_content = markdown.markdown(file_content)

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取纯文本内容
    text_content = soup.get_text()

    # 用于存储结果的变量
    extracted_content = f"提取的文本内容：\n{text_content}\n\n"

    # 提取图片并进行OCR
    images = soup.find_all('img')
    ocr_results = []
    print(uploaded_images)

    for img in images:
        img_path = img['src']
        
        # 判断是本地图片还是网络图片
        if img_path.startswith('http://') or img_path.startswith('https://'):
            # 处理网络图片
            try:
                response = requests.get(img_path)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                print(f"处理网络图片: {img_path}")
            except requests.exceptions.RequestException as e:
                print(f"无法下载图片: {img_path}. 错误: {e}")
                continue
        else:
            # 处理本地上传的图片
            print(img_path)
            if img_path in uploaded_images:
                try:
                    image = Image.open(uploaded_images[img_path])
                    print(f"处理本地图片: {img_path}")
                except Exception as e:
                    print(f"无法打开本地图片: {img_path}. 错误: {e}")
                    continue
            else:
                print(f"找不到本地图片: {img_path}")
                continue
        
        # 使用 img_loader 函数进行 OCR 识别
        try:
            text = img_loader(image)  # 调用 img_loader 函数，返回纯文本
            ocr_results.append((img_path, text))
        except Exception as e:
            print(f"无法对图片进行OCR: {img_path}. 错误: {e}")

    # 将OCR结果加入文本
    if ocr_results:
        extracted_content += "从图片中提取的文字：\n"
        for img_path, ocr_text in ocr_results:
            extracted_content += f"图片路径: {img_path}\n提取的文字:\n{ocr_text}\n\n"

    # 提取表格数据
    tables = soup.find_all('table')
    table_data = []

    for table in tables:
        headers = [th.get_text().strip() for th in table.find_all('th')]
        rows = []

        for tr in table.find_all('tr'):
            cells = [td.get_text().strip() for td in tr.find_all('td')]
            if cells:
                rows.append(cells)

        table_data.append((headers, rows))

    # 将表格数据加入文本
    if table_data:
        extracted_content += "提取的表格数据：\n"
        for headers, rows in table_data:
            extracted_content += f"表头: {' | '.join(headers)}\n"
            for row in rows:
                extracted_content += f"行: {' | '.join(row)}\n"
            extracted_content += "\n"
    extracted_content = clean_text(extracted_content)
    return extracted_content


if __name__ == "__main__":
    markdown_file_path = '../test_file/mine/table.md'  # 替换为你的Markdown文件路径
    
    with open(markdown_file_path, 'r', encoding='utf-8') as md_file:
        file_content = md_file.read()
    
    extracted_content = test(file_content)
    
    print(extracted_content)
