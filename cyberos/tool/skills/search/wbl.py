### Build Index

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

### from langchain_cohere import CohereEmbeddings

# Set embeddings

# Docs to index
urls = [
    "https://griseo.nimo.page/about.html",
    "https://www.zhihu.com/question/500135527/answer/2656145759",
]

# Load
docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# Split

text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)

doc_splits = text_splitter.split_documents(docs_list)

print(doc_splits)
print(docs)
# Add to vectorstore
# vectorstore = Chroma.from_documents(
#     documents=doc_splits,
#     collection_name="rag-chroma",
#     embedding=embd,
# )
# retriever = vectorstore.as_retriever()