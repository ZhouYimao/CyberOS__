"""
基于各类规则
处理以SystemMessage为代表的Message

更新的函数也可以写里面
"""
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 真正的代码

from cyberos.settings.prompts import SYSTEM_MESSAGE_TEMPLATE
from cyberos.settings.configs import CYBEROS, USER_ID

import os
import json

CONFIG = os.path.join(CYBEROS, 'data', USER_ID, 'config.json')
TODO = os.path.join(CYBEROS, 'data', USER_ID, 'todo.json')


def system_message() -> str:
    # 读取 config.json 文件
    with open(CONFIG, 'r') as fr:
        config_data = json.load(fr)

    # 获取 persona 和 core_memory
    persona = config_data.get("persona", "")
    core_memory = config_data.get("core_memory", {})

    # 将 core_memory 格式化为一个字符串，便于插入模板
    formatted_core_memory = "\n".join([f"{key}: {value}" for key, value in core_memory.items()])

    # 读取 todo.json 文件
    with open(TODO, 'r') as fr:
        todo_data = json.load(fr)

    # 提取 task 和 trigger 信息并格式化
    formatted_todo_list = "\n".join([f"Task: {item['task']}, 触发条件: {item['trigger']}" for item in todo_data])

    # 格式化 SYSTEM_MESSAGE_TEMPLATE
    system_message = SYSTEM_MESSAGE_TEMPLATE.format(persona, formatted_core_memory, formatted_todo_list)

    return system_message


SYSTEM_MESSAGE = system_message()
# 使用示例

# window = {}
# 几类window - 比如记忆

# 还有tree or dag

# 需要一个函数.single node(agent)需要什么样的记忆


if __name__ == "__main__":
    print(SYSTEM_MESSAGE)
