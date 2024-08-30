from paddleocr import PaddleOCR
from paddle import set_device
from PIL import Image
from text_utils import clean_text, clarify_text
import requests
import cv2
import numpy as np
import os

def extract_text_from_image(img_path, clarify_flag=False, lang='ch'):
    """
    使用 PaddleOCR 提取图像中的文本。
    
    参数:
    - img_path: 图像文件的路径或 URL
    - clarify_flag: 是否对提取的文本进行逻辑梳理
    - lang: 语言模型（默认是中文 "ch"）
    
    返回:
    - 提取的纯文本字符串
    """
    # 设置 CPU 为推理设备
    set_device('cpu')

    # 初始化 PaddleOCR 模型
    ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)

    # 判断 img_path 是 URL 还是本地路径
    if img_path.startswith('http://') or img_path.startswith('https://'):
        response = requests.get(img_path)
        image_np = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    else:
        # 读取本地图像
        image = cv2.imread(img_path)

    # 使用 OCR 识别图像中的文本
    result = ocr.ocr(image, cls=True)

    # 提取文本并组织成纯文本
    extracted_text = " ".join(line[1][0] for res in result for line in res)

    extracted_text = clean_text(extracted_text)
    
    if clarify_flag:  # 针对思维导图，逻辑图
        extracted_text = clarify_text(extracted_text).content
        
    return extracted_text

def img_loader(file_name: str,clarify_flag=False):
    text = extract_text_from_image(file_name, clarify_flag)
    return text

if __name__ == "__main__":
    file_name = '../test_file/mine/thinkAny.webp'
    print(img_loader(file_name))