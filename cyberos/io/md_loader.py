from langchain_community.document_loaders import UnstructuredMarkdownLoader

loader = UnstructuredMarkdownLoader(
    "./agent.md",
    mode="single",
    strategy="fast",
)

docs = loader.load()
print(docs[0])