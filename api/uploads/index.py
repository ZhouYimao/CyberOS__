import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 真正的代码
from api.jwt import verify_jwt
from fastapi import APIRouter, HTTPException, File, UploadFile, Depends, Body, status
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# 定义上传的响应模型
class UploadResponse(BaseModel):
    id: str
    object: str
    bytes: int
    created_at: int
    filename: str
    purpose: str
    status: str
    expires_at: int
    file: Optional[dict] = None  # 仅在上传完成时存在

class UploadPartResponse(BaseModel):
    id: str
    object: str
    created_at: int
    upload_id: str



def setup_uploads_index_router():
    @router.post("/uploads", tags=["uploads"], response_model=UploadResponse)
    async def create_upload(
        purpose: str = Body(..., description="The purpose of the upload"),
        filename: str = Body(..., description="The name of the file"),
        bytes: int = Body(..., description="Size of the file in bytes"),
        mime_type: str = Body(..., description="MIME type of the file"),
        user_id: str = Depends(verify_jwt)
    ):
        """
        创建上传任务。
        """
        try:
            ...
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/uploads/{upload_id}/parts", tags=["uploads"], response_model=UploadPartResponse)
    async def send_file_data(
        upload_id: str,
        file: UploadFile = File(...),
        user_id: str = Depends(verify_jwt)
    ):
        """
        上传文件的一部分。
        """
        try:
            ...
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/uploads/{upload_id}/complete", tags=["uploads"], response_model=UploadResponse)
    async def complete_upload(
        upload_id: str,
        part_ids: List[str] = Body(..., description="List of part IDs"),
        user_id: str = Depends(verify_jwt)
    ):
        """
        确认上传完成。
        """
        try:
            ...
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/uploads/{upload_id}/cancel", tags=["uploads"], response_model=UploadResponse)
    async def cancel_upload(
        upload_id: str,
        user_id: str = Depends(verify_jwt)
    ):
        """
        取消上传任务。
        """
        try:
            ...
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
   
    
    return router

