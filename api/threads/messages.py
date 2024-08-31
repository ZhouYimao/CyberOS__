import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 真正的代码
from api.jwt import verify_jwt
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
from pydantic import BaseModel


router = APIRouter()

# 定义响应模型
class MessageContent(BaseModel):
    type: str
    text: dict

class MessageResponse(BaseModel):
    id: str
    object: str
    created_at: int
    assistant_id: Optional[str]
    thread_id: str
    run_id: Optional[str]
    role: str
    content: List[MessageContent]
    attachments: List = []
    metadata: dict

class MessageListResponse(BaseModel):
    object: str
    data: List[MessageResponse]
    first_id: str
    last_id: str
    has_more: bool

class DeleteMessageResponse(BaseModel):
    id: str
    object: str
    deleted: bool

def setup_threads_messages_router():
    @router.post("/threads/{THREAD_ID}/messages", tags=["threads"], response_model=MessageResponse)
    def send_messages_to_agent_in_threads(
        THREAD_ID: str,
        role: str = Body(..., description="Role of the message sender, e.g., 'user'"),
        content: str = Body(..., description="Content of the message"),
        jwt: str = Depends(verify_jwt)
    ):
        """
        Create a message in a specific thread.
        """
        try:
            ...
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating message: {str(e)}")

    @router.get("/threads/{THREAD_ID}/messages", tags=["threads"], response_model=MessageListResponse)
    def get_threads_messages(
        THREAD_ID: str,
        user_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = 100,
        jwt: str = Depends(verify_jwt)
    ):
        """
        List messages in a specific thread.
        """
        try:
            ...
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

    @router.get("/threads/{THREAD_ID}/messages/{MESSAGE_ID}", tags=["threads"], response_model=MessageResponse)
    def retrieve_a_message(THREAD_ID: str, MESSAGE_ID: str, jwt: str = Depends(verify_jwt)):
        """
        Retrieve a specific message by message ID.
        """
        try:
            # 获取消息
            #if 没获取到
                raise HTTPException(status_code=404, detail="Message not found.")
            #return 获取结果
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving message: {str(e)}")
    
    @router.delete("/threads/{THREAD_ID}/messages/{MESSAGE_ID}", tags=["threads"], response_model=DeleteMessageResponse)
    def delete_a_message(THREAD_ID: str, MESSAGE_ID: str, jwt: str = Depends(verify_jwt)):
        """
        Delete a specific message by message ID.
        """
        try:
            # 寻找并删除
            #if 没找到:
                raise HTTPException(status_code=404, detail="Message not found.")
            #return DeleteMessageResponse(id=MESSAGE_ID, object="thread.message.deleted", deleted=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting message: {str(e)}")

    return router
