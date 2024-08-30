from PIL import Image
import pytesseract
from text_utils import clean_text
# 指定Tesseract的安装路径，如果Tesseract在系统PATH中则不需要
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # 适用于Windows
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # 适用于Linux/macOS

def ocr_from_image(image_path):
    # 打开图片文件
    image = Image.open(image_path)
    
    # 对图片进行OCR操作
    text = pytesseract.image_to_string(image, lang='chi_sim')  # 指定语言为英语，根据需要可以更改语言代码
    
    # 返回提取的文字
    return text

# 图片文件的路径
image_path = './wechat.png'

# 调用函数并打印结果
extracted_text = ocr_from_image(image_path)

extracted_text = clean_text(extracted_text)
print(extracted_text)