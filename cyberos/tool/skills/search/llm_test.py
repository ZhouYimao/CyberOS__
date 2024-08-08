import imp
from langchain_community.chat_models import ChatOpenAI
from search import search
### Build Index

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings




llm = ChatOpenAI(
    model="qwen2-instruct",
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8011/v1",
    temperature=0,
)


def main():
    query_list = []
    query1 = "2024年欧洲杯结果怎么样"
    query_list.append(query1)
    result_num = 10
    google_results = search(query_list,result_num)
    order=0
    context=''
    for google_result in google_results:
        order +=1 
        snippet = google_result.get('snippet')
        context +=f'{order}.{snippet}\n'
    basic_prompt=f"""
    You are a large language AI assistant built. You are given a user question, and please write clean, concise and accurate answer to the question. You will be given a set of related contexts to the question, each starting with a reference number like [[citation:x]], where x is a number. Please use the context and cite the context at the end of each sentence if applicable.

    Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. Say "information is missing on" followed by the related topic, if the given context do not provide sufficient information.

    Please cite the contexts with the reference numbers, in the format [citation:x]. If a sentence comes from multiple contexts, please list all applicable citations, like [citation:3][citation:5]. Other than code and specific names and citations, your answer must be written in the same language as the question.

    Here are the set of contexts:

    {context}

    Remember, don't blindly repeat the contexts verbatim. And here is the user question:
    {query_list[0]}
    """
    llm_response=llm.invoke(basic_prompt)
    print(llm_response)



if __name__ == "__main__":
    main()
