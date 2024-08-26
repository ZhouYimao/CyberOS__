import re 
from unstructured.cleaners.core import clean, clean_non_ascii_chars
# 清洗文本的函数
def clean_text(text):
    # 删除大段空格和换行
    text = clean(text = text ,
                 bullets = True,
                 extra_whitespace = True,)
    # 删除引文，如 [1]、[2] 等
    text = re.sub(r'\[\d+\]', '', text)
    # 去除 < > 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 使用正则表达式的 sub 函数替换掉所有 "- " 的实例
    text = re.sub(r'-\s', '', text)
    # 删除连续的制表符\t
    text = re.sub(r'\t+', ' ', text)  # 将连续的制表符替换为单个空格
    return text.strip()