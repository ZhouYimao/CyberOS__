"""
api整体框架还需完善的部分：
1、每个api接口函数体的实现
2、错误码设置
3、api调用完成后返回数据类的设置
4、进一步完善后端可能需要完善与服务器的交互逻辑（有时同步、有事异步），包括对服务器各种接口状态的管理

个人这边待解决的问题：
1、upload形式待确认
"""
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 真正的代码

from fastapi import APIRouter,HTTPException
import uvicorn
from fastapi.staticfiles import StaticFiles
from api.memorys.config import setup_memorys_config_router
from api.memorys.todo import setup_memorys_todo_router
from api.openai_chat_completions.chat_completions import setup_openai_chat_completions_router
from api.threads.index import setup_threads_index_router
from api.threads.messages import setup_threads_messages_router
from api.uploads.index import setup_uploads_index_router

V1_PREFIX= "/v1"

app=FastAPI()

#将路由与app绑定
app.include_router(setup_memorys_config_router(),prefix=V1_PREFIX)
app.include_router(setup_memorys_todo_router(),prefix=V1_PREFIX)
app.include_router(setup_openai_chat_completions_router(),prefix=V1_PREFIX)
app.include_router(setup_threads_index_router(),prefix=V1_PREFIX)
app.include_router(setup_threads_messages_router(),prefix=V1_PREFIX)
app.include_router(setup_uploads_index_router(),prefix=V1_PREFIX)

#用来绑定服务器中的静态文件
#app.mount("/static",StaticFiles(directory="静态文件名_代更改"))


if __name__=='__main__':
    uvicorn.run(app, port=8080, reload=True)
