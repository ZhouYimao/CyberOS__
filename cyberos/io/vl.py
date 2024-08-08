from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="step-1v-8k",
                   openai_api_key="7vXrtOZIC0uLPGZGMtvQzX1HEgrZude0i75sAtLjMe86wznqEEOKn4puI1YaBRkLx",
                   openai_api_base="https://api.stepfun.com/v1",
                   temperature=0.7,)

import base64

import httpx

image_data = base64.b64encode(httpx.get("https://bkimg.cdn.bcebos.com/pic/b03533fa828ba61ea8d3e812c263800a304e251ff3cd?x-bce-process=image/format,f_auto/watermark,image_d2F0ZXIvYmFpa2UyNzI,g_7,xp_5,yp_5,P_20/resize,m_lfit,limit_1,h_1080").content).decode("utf-8")

# with open('/home/sjtu/zyk_file/LLM/1.png', 'rb') as file:
#     # 读取文件内容
#     image_content = file.read()
#     # 对文件内容进行Base64编码
#     image_data = base64.b64encode(image_content).decode("utf-8")

message = HumanMessage(
    content=[
        {"type": "text", "text": "图中的是什么季节"},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
        },
    ],
)
response = model.invoke([message])
print(response.content)
