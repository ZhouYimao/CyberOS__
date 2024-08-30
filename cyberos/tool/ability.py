import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

import json
from typing import Dict

from datetime import datetime

from cyberos.settings.configs import CYBEROS, USER_ID

from cyberos.storage.graph_db import retrieve

CONFIG = os.path.join(CYBEROS, 'data', USER_ID, 'config.json')
TODO = os.path.join(CYBEROS, 'data', USER_ID, 'todo.json')


def update_persona(persona: str) -> str:
    """
    当用户明确需要你修改人设时，调用此函数
    :param persona: 更新后的人设，必须是全文
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
        update_core_memory("生日: 2012-12-21, 电话: 19198101145, 职业: 学生")
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


def retrieve_memory(question: str) -> str:
    """
    回忆历史对话，
    如果当前对话需要结合过往记忆、缺失上下文时。
    或者个性化聊到个性化的内容时，调用该工具从聊天记录中检索过往记忆；
    比如用户问：我明天需要吃什么、你觉得谁来做市场比较合适。
    请记住，这些仅仅基于图数据库检索的聊天记录总结，其中不一定含有你想要的答案。

    :param question: 需要检索的问题
    :type question: str

    :return: 与该问题最相关的一些三元组和对话记录
    :rtype: str
    """

    return retrieve(question)


"""
2、replan很重要，挂起todo 的时候每一步都可能要replan，其实就是检查那些小步骤有没有要增、改、删的
（multiagent管理上下文；进入任务状态的时候，开一个agent来通信）
"""


def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def external_function_for_plan(task, trigger):
    # 占位函数: 在 plan=True 时调用的外部函数
    # 这里可以根据你的需求实现相应的逻辑
    pass


def update_task(task: str = None, trigger: str = None, completed: bool = False, plan: bool = False) -> str:
    """
    更新或添加任务到TODO中。若task和TODO中的任务名称相同，则更新trigger和completed时必须传入**完全同名的**task。
    
    :param task: 任务名称（隐含主语是你，例如用户提到明晚看电影，任务名称应当是提醒用户看电影）
    :param trigger: 触发条件（应当是语境、语义的，不应当是闹钟式的，因为会在子任务中体现）正确示例：周溢茂回家后；错误示例：晚上8点
    :param completed: 任务完成True，未完成False    
    :param plan: 是否需要进一步的规划拆解成子任务或完成子任务后更新状态,True or False
    :return: 更新状态信息
    
    示例:
        update_task(task="协同设计用户界面", trigger="和帅哲见面后", plan=True)  # 新建需要plan的任务
        update_task(task="协同设计用户界面", trigger="和帅哲见面前")  # 更改Trigger
        update_task(task="协同设计用户界面", completed=False, plan=True)  # 重新规划（完成某个子任务后也需要）
        update_task(task="协同设计用户界面", completed=True, plan=False)  # 标记任务完成
        update_task(task="提醒周溢茂开会", trigger="周溢茂回家后",plan=False)  # 新建无需plan的任务
    """

    # 处理文件为空或不存在的情况
    if not os.path.exists(TODO) or os.stat(TODO).st_size == 0:
        todo_data = []
    else:
        with open(TODO, "r", encoding="utf-8") as fr:
            try:
                todo_data = json.load(fr)
            except json.JSONDecodeError:
                return "todo.json 文件格式错误或为空，无法解析。"

    task_found = False

    # 查找是否已存在相同任务
    for item in todo_data:
        if task and item['task'] == task:
            task_found = True
            if trigger:
                item['trigger'] = trigger
            if completed is not None:
                item['completed'] = completed
            break

    # 如果任务未找到，且task和trigger都存在，则创建新任务
    if not task_found and task and trigger:
        new_task = {
            "task": task,
            "trigger": trigger,
            "completed": completed,
            "createdat": get_current_timestamp(),
            "subtasks": []
        }
        todo_data.append(new_task)

    # 调用外部函数当plan=True时
    if plan:
        external_function_for_plan(task, trigger)

    # 写回json文件
    with open(TODO, "w", encoding="utf-8") as fw:
        json.dump(todo_data, fw, ensure_ascii=False, indent=4)

    return "任务已更新" if task_found else "新任务已添加"

# 示例使用
# print(update_task(task="设计用户界面",trigger="和帅哲见面后"))
# print(update_task(task="设计用户界面",trigger="和帅哲见面前"))
# print(update_task(task="设计用户界面",completed=True))
# print(update_task(task="设计后端",trigger="八月三号之后"))
