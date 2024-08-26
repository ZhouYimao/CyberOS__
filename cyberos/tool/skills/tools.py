import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from cyberos.settings.configs import CYBEROS
from cyberos.tool.skills.search.brief_search import search


def extract_todo_item(info: str) -> str:
    """
    当用户提及与未来计划、任务、规划、需要完成的事项等相关的信息,且有明确时间相关的词语时(如"明天"、"下周"、"月底前"等),调用此工具，更新待办事项列表(To-Do List)
    新的待办事项会被添加到现有列表中，待办事项的具体内容包括:
        1.类型(Type): 任务的大致类别（如工作、个人、学习、健康等）
        2.内容(Content): 任务的具体描述
        3.截止日期(Deadline): 任务的完成日期或时间范围
        4.详细规划(Planning): 是否需要进一步的规划或分析
    额外规则：
        1. 当用户明确提到"我该怎么"、"为我推荐"、"帮我规划"、"需要详细计划"、"帮我分析如何完成该任务"等类似地指向更深层次任务细节的信息时,将Planning设置为'是',未明确提到时设置为'否'。
        2. 将相对日期(如："下周五"、"这周日"、"下个月")，转换为具体日期。
        3. Planning的值仅存在2种情况:'是'或'否'。
        4. 待办事项的4项具体内容必须全部存在。
        5. 你需要根据任务内容自行判断适当的类型,当你无法准确定义任务的大致类别时,将Type设置为其它。
        6. 你需要将内容进行适当改写,去除口语化表达,使用准确、精炼的书面化语言,同时不能遗漏关键信息,也不能自行增添信息,地点等关键信息一定要保留,时间信息不必再保留。

        
    :param info: 用户关键信息
    :type info: str
    :return: 更新状态信息
    :rtype: str
    
    示例:
        extract_todo_item("Type: 工作\nContent: 完成关于CyberLife的项目报告\nDeadline: 明天早上\nType:否")
        extract_todo_item("Type: 工作\nContent: 完成一个AIOS项目\nDeadline: 下个月\nType:是")    
    """
    file_path = os.path.join(CYBEROS, "preset", "to_do_list.txt")
    with open(file_path, "w") as fw:
        fw.write(info)


def web_search(init_query: str) -> list:
    """
    当你需要访问超出知识限制的信息，如时效性信息（新闻事件、最新技术），地域性信息时，
    需要调用 web_search 进行联网搜索。
    该函数会返回 snippet, url 以及 url 对应的文本内容等重要信息，帮助你回答问题。

    :param init_query: 用户提出的初始问题
    :type init_query: str

    :return:
        list: 一个包含'url'、'name'、'snippet'以及'id'(搜索结果的编号)4项的字典列表即all_search_results。
        其中snippet是搜索结果的关键信息,对你回答用户的问题非常有帮助;url可能用于further_search。
    :rtype: list
    """
    return search(init_query)


if __name__ == "__main__":
    search("如何在langchain中调用工具？")
