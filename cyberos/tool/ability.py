import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)


import json
from typing import Dict
from cyberos.settings.configs import CYBEROS

USER_ID = "3367964d-5f5f-7008-1dd1dfa2e155"
CONFIG = os.path.join(CYBEROS, 'data', USER_ID, 'config.json')

def update_persona(persona: str) -> str:
    """
    当用户明确需要你修改人设时，调用此函数
    :param persona: 修改的人设内容(必须是全文)
    :type persona: str
    示例:
        update_persona("我是名侦探柯南，我喜欢解谜，我是一个聪明的人")
    """

    with open(CONFIG, "r", encoding="utf-8") as fr:
        config_data = json.load(fr)
    
    config_data["persona"] = persona

    with open(CONFIG, "w", encoding="utf-8") as fw:
        json.dump(config_data, fw, ensure_ascii=False, indent=4)

    return "你的人设已经更新，现在你需要按照人设进行回答"


def update_core_memory(info: str) -> str:
    """
    当用户提及自己的姓名、年龄、性别、生日、联系方式、教育经历、职业等信息时，更新核心记忆。
    新信息会追加或更新到现有信息中，而不是完全覆盖。
    如果某项信息的值为空，该项将被忽略（不会删除已存在的信息）。

    :param info: 用户关键信息
    :type info: str
    :return: 更新状态信息
    :rtype: str

    示例:
        update_core_memory("姓名: 格蕾修, 年龄: 12, 性别: 女")
        update_core_memory("生日: 2012-12-21, 联系方式: 19198101145, 职业: 学生")
    """
    with open(CONFIG, "r", encoding="utf-8") as fr:
        config_data = json.load(fr)

    core_memory = config_data.get("core_memory", {})

    # 解析新的信息
    new_info: Dict[str, str] = {}
    for item in info.split(', '):
        key, value = item.split(': ')
        if value.strip():  # 只有在值不为空字符串时才添加
            new_info[key] = value.strip()

    # 更新现有信息
    core_memory.update(new_info)

    config_data["core_memory"] = core_memory

    # 将更新后的信息写入文件
    with open(CONFIG, "w", encoding="utf-8") as fw:
        json.dump(config_data, fw, ensure_ascii=False, indent=4)

    return "更新完毕"

# def retrieve_memory(question: str) -> str:
#     """
#     回忆历史对话，
#     如果当前对话需要结合过往记忆、缺失上下文时。
#     或者个性化聊到个性化的内容时，调用该工具从聊天记录中检索过往记忆；
#     比如用户问：我明天需要吃什么、你觉得谁来做市场比较合适。
#     请记住，这些仅仅基于图数据库检索的聊天记录总结，其中不一定含有你想要的答案。

#     :param question: 需要检索的问题
#     :type question: str

#     :return: 与该问题最相关的一些三元组和对话记录
#     :rtype: str
#     """

#     return retrieve(question)
