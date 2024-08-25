from cleaning import clean_text
from langchain_community.document_loaders import PyPDFLoader
def pdf_loader(pdf_path: str):
    loader = PyPDFLoader(pdf_path, extract_images=True)
    pages = loader.load()
    metadata = pages[0].metadata
    # 初始化一个空字符串来存储整个文档的文本
    full_text = ""
    for page_number in range(len(pages)):
        content = pages[page_number].page_content
        cleaned_text = clean_text(content)
        full_text += (cleaned_text + '\n\n') # 添加换行符以分隔不同页面的文本
    return full_text