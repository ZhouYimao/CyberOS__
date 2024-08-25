from langchain_community.document_loaders import Docx2txtLoader
from cleaning import clean_text
# 这里的file_name就是完整路径
def docx_loader(filename:str):
    loader = Docx2txtLoader(filename)
    data = loader.load()
    text = clean_text(data[0].page_content)
    return text