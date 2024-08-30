import re
from unstructured.cleaners.core import clean, clean_non_ascii_chars
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from cyberos.settings.configs import ModelConfig

llm = ModelConfig().llm

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

def clarify_text(input_text):
    prompt = f"""请将以下混乱的文字重新组织,确保逻辑顺序正确，并划分出合理的层次结构，并以 Markdown 样式输出。仅能使用已有的文字，不能添加任何新信息，不需要用自然语言连接。必要时可以使用序号或列表。

    需要整理的内容如下：

    {input_text}

    请输出整理后的文本，以 Markdown 格式表示。"""

    response = llm.invoke(prompt)
    return response

def test_clarify_text(input_text):
    prompt = f"""
    请根据输入文本的情况判断其内容是否混乱。如果内容逻辑清晰、结构合理，请不要做任何改动，直接返回原始文本。

    如果内容比较混乱，请重新组织文本，确保逻辑顺序正确，并划分出合理的层次结构，并以 Markdown 样式输出。
    
    仅能使用已有的文字，不能添加任何新信息，不需要用自然语言连接，同时不能遗漏任何信息。必要时可以使用序号或列表。

    需要整理的内容如下：

    {input_text}

    请根据需要输出原始文本或重新组织后的 Markdown 结构。"""

    response = llm.invoke(prompt)
    return response

if __name__ == "__main__":
    input_text = '在改进网络1/O模型前，我先来提一个问题，你知道服务器单机理论最大能连接多少个客户端？ 相信你知道TCP连接是由四元组唯一确认的，这个四元组就是：本机IP，本机端口，对端IP，对端端口 服务器作为服务方，通常会在本地固定监听一个端口，等待客户端的连接。因此服务器的本地IP和端口 是固定的，于是对于服务端TCP连接的四元组只有对端IP和端口是会变化的，所以最大TCP连接数=客 户端IP数?客户端端口数 对于IPv4，客户端的IP数最多为2的32次方，客户端的端口数最多为2的16次方，也就是服务端单机 最大TCP连接数约为2的48次方 这个理论值相当“丰满”，但是服务器肯定承载不了那么大的连接数，主要会受两个方面的限制： ·文件描述符，Socket实际上是一个文件，也就会对应一个文件描述符。在Linux下，单个进程打开的 文件描述符数是有限制的，没有经过修改的值一般都是1024，不过我们可以通过ulimit增大文件描述 符的数目； 系统内存，每个1CP连接在内核中都有对应的数据结构，意味看每个连接都是会占用一定内存的 那如果服务器的内存只有2GB，网卡是干兆的，能支持并发1方请求吗？ 并发1万请求，也就是经典的C10K问题，C是Client单词首字母缩写，C10K就是单机同时处理1万个 请求的问题。 从硬件资源角度看，对于2GB内存干兆网卡的服务器，如果每个请求处理占用不到200KB的内存和 100Kbit的网络带宽就可以满足并发1万个请求 不过，要想真正实现C10K的服务器，要考虑的地方在于服务器的网络1/O模型，效率低的模型，会加重 系统开销，从而会离C10K的目标越来越远。'
    clarified_text = test_clarify_text(input_text)
    print(clarified_text.content)