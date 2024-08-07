from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI

# from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

CYBEROS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

# 单例模式用于模型配置
class ModelConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelConfig, cls).__new__(cls, *args, **kwargs)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        # 加载 .env 文件
        load_dotenv()
        
        # 导入 .env 文件中的变量作为类属性
        self.BASE_LANGUAGE_MODEL = os.getenv('BASE_LANGUAGE_MODEL')
        self.LLM_API_KEY = os.getenv('LLM_API_KEY')
        self.LLM_URL = os.getenv('LLM_URL')

        self.BASE_EMBEDDING_MODEL = os.getenv('BASE_EMBEDDING_MODEL')
        self.EMBEDDING_API_KEY = os.getenv('EMBEDDING_API_KEY')
        self.EMBEDDING_URL = os.getenv('EMBEDDING_URL')
        
        self.llm = ChatOpenAI(model=self.BASE_LANGUAGE_MODEL, 
                         api_key=self.LLM_API_KEY, 
                         base_url=self.LLM_URL)



# 单例模式用于数据库配置
class DatabaseConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConfig, cls).__new__(cls, *args, **kwargs)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        # 加载 .env 文件
        load_dotenv()
        
        # 导入 .env 文件中的变量作为类属性
        self.GRAPH_DB_USERNAME = os.getenv('GRAPH_DB_USERNAME')
        self.GRAPH_DB_PASSWORD = os.getenv('GRAPH_DB_PASSWORD')
        self.GRAPH_DB_URL = os.getenv('GRAPH_DB_URL')

        # # 初始化 Neo4j 配置
        # self.graph_store = Neo4jPropertyGraphStore(
        #     username=self.GRAPH_DB_USERNAME,
        #     password=self.GRAPH_DB_PASSWORD,
        #     url=self.GRAPH_DB_URL,
        # )

# 测试配置
if __name__ == '__main__':
    # 测试模型配置
    model_config = ModelConfig()
    print(model_config.BASE_LANGUAGE_MODEL)

    # 测试数据库配置
    db_config = DatabaseConfig()
    print(db_config.GRAPH_DB_URL)