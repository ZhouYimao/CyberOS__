import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 真正的代码
from api.jwt import verify_jwt
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
import requests

router = APIRouter()

# Pydantic 数据模型，用于请求和响应的数据验证
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]

class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[dict]
    usage: dict


def setup_openai_chat_completions_router():
    @router.post("/chat/completions", tags=["chat_completions"], response_model=ChatCompletionResponse)
    async def create_chat_completion(
        chat_request: ChatCompletionRequest, user_id: str = Depends(verify_jwt)#若verify_jwt执行的结果抛出了错误码，则该路由不会执行
    ):
        ...



    return router