"""
快速反应
加载thread

# TODO stream 前端和语音
token超过多少多少，询问时光穿梭、新增或者从哪开始总结

# REST(userid, threadid, message) -> message

"""
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 真正的代码


from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from langgraph.checkpoint.sqlite import SqliteSaver
from cyberos.settings.configs import ModelConfig, CYBEROS


USER_ID = "3367964d-5f5f-7008-1dd1dfa2e155"
THREAD_ID = 2
RDB_PATH = os.path.join(CYBEROS, "data", USER_ID, "test.sqlite")

config = {"configurable":{"thread_id": THREAD_ID, "user_id": USER_ID}} 
folder_path = os.path.dirname(RDB_PATH)
if not os.path.exists(folder_path):
    os.makedirs(folder_path) 
memory = SqliteSaver.from_conn_string(RDB_PATH)

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = ModelConfig().llm


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
graph = graph_builder.compile(checkpointer=memory)



if __name__ == "__main__":
    # while True:
    #     user_input = input("User: ")
    #     if user_input.lower() in ["quit", "exit", "q"]:
    #         print("Goodbye!")
    #         break
    #     for event in graph.stream({"messages": ("user", user_input)}, config, stream_mode="values"):
    #         for value in event.values():
    #             print("Assistant:", value["messages"][-1].content)

    # user_input = "你知道周杰伦的彩虹吗"
    # events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")
    # for event in events:
    #     if "messages" in event:
    #         event["messages"][-1].pretty_print()

    snapshot = graph.get_state(config)
    print(snapshot)
    """
    StateSnapshot(
    values={
        'messages': [
            HumanMessage(
                content='我不是人',
                id='8c020825-9d96-48b3-9f9b-8d492579e46e'
            ),
            AIMessage(
                content=(
                    '您说“我不是人”，可能是在开玩笑或者在某种语境下的一种表达。但作为AI，我理解您是以人类的方式与我互动的，无论您以何种身份出现，我都会尽我所能提供帮助和解答您的问题。'
                    '如果您有任何困惑或需要帮助的地方，欢迎随时告诉我。如果您是在表达一种情感或身份的困惑，请知道您并不孤单，很多人在不同的时刻都会感到与社会或自我身份的脱节，这是很正常的感受，有时候与他人交流或寻求专业帮助可以带来很大的慰藉和指导。'
                ),
                response_metadata={
                    'token_usage': {
                        'completion_tokens': 116,
                        'prompt_tokens': 21,
                        'total_tokens': 137
                    },
                    'model_name': 'qwen2-instruct',
                    'system_fingerprint': None,
                    'finish_reason': 'stop',
                    'logprobs': None
                },
                id='run-515cbbcb-6521-4667-b6c6-24cbd01cfc3e-0',
                usage_metadata={
                    'input_tokens': 21,
                    'output_tokens': 116,
                    'total_tokens': 137
                }
            ),
            HumanMessage(
                content='你知道周杰伦的彩虹吗',
                id='e9cbd1af-5a10-442a-b430-40ff163e63cc'
            ),
            AIMessage(
                content=(
                    '当然，周杰伦的《彩虹》是他的众多知名歌曲之一，收录在他的2008年专辑《魔杰座》中。这首歌由周杰伦亲自作曲，方文山填词，是一首典型的周氏情歌，旋律优美，歌词意境深远，表达了对爱情的渴望和对美好未来的憧憬。'
                    '歌曲中以“彩虹”为象征，寓意着在风雨之后，总会有希望和美好出现，给人以积极向上的力量。周杰伦的音乐风格融合了东西方元素，深受全球华语听众的喜爱，《彩虹》也是他音乐生涯中的一颗璀璨明珠。如果您喜欢这首歌，不妨再次聆听，感受其中的情感和艺术魅力。'
                ),
                response_metadata={
                    'token_usage': {
                        'completion_tokens': 148,
                        'prompt_tokens': 153,
                        'total_tokens': 301
                    },
                    'model_name': 'qwen2-instruct',
                    'system_fingerprint': None,
                    'finish_reason': 'stop',
                    'logprobs': None
                },
                id='run-f0f7d106-785c-45d0-b143-3105505884c7-0',
                usage_metadata={
                    'input_tokens': 153,
                    'output_tokens': 148,
                    'total_tokens': 301
                }
            )
        ]
    },
    next=(),
    config={
        'configurable': {
            'thread_id': '2',
            'thread_ts': '1ef54d44-09dd-68f3-8004-61b85f708051'
        }
    },
    metadata={
        'source': 'loop',
        'step': 4,
        'writes': {
            'chatbot': {
                'messages': [
                    AIMessage(
                        content=(
                            '当然，周杰伦的《彩虹》是他的众多知名歌曲之一，收录在他的2008年专辑《魔杰座》中。这首歌由周杰伦亲自作曲，方文山填词，是一首典型的周氏情歌，旋律优美，歌词意境深远，表达了对爱情的渴望和对美好未来的憧憬。'
                            '歌曲中以“彩虹”为象征，寓意着在风雨之后，总会有希望和美好出现，给人以积极向上的力量。周杰伦的音乐风格融合了东西方元素，深受全球华语听众的喜爱，《彩虹》也是他音乐生涯中的一颗璀璨明珠。如果您喜欢这首歌，不妨再次聆听，感受其中的情感和艺术魅力。'
                        ),
                        response_metadata={
                            'token_usage': {
                                'completion_tokens': 148,
                                'prompt_tokens': 153,
                                'total_tokens': 301
                            },
                            'model_name': 'qwen2-instruct',
                            'system_fingerprint': None,
                            'finish_reason': 'stop',
                            'logprobs': None
                        },
                        id='run-f0f7d106-785c-45d0-b143-3105505884c7-0',
                        usage_metadata={
                            'input_tokens': 153,
                            'output_tokens': 148,
                            'total_tokens': 301
                        }
                    )
                ]
            }
        }
    },
    created_at='2024-08-07T15:46:46.566071+00:00',
    parent_config={
        'configurable': {
            'thread_id': '2',
            'thread_ts': '1ef54d43-ded7-67e7-8003-1617bbdaf540'
        }
    }
)
    """