import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 真正的代码
from api.jwt import verify_jwt
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List
from pydantic import BaseModel
from uuid import uuid4


router = APIRouter()

# 定义response model类
class FileResponse(BaseModel):
    id: str
    object: str
    bytes: int
    created_at: int
    filename: str
    purpose: str

class DeleteFileResponse(BaseModel):
    id: str
    object: str
    deleted: bool

class ListFilesResponse(BaseModel):
    data: List[FileResponse]
    object: str

def setup_files_index_router():
    @router.get("/files", tags=["files"], response_model=ListFilesResponse)
    def list_files(user_id: str = Depends(verify_jwt)):
        """
        List all files uploaded by the user
        """
        try:
           ...
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

    @router.post("/files/markdowns", tags=["files"], response_model=FileResponse)
    async def upload_files(
        purpose: str = "user-uploaded-markdown",
        file: UploadFile = File(...),
        user_id: str = Depends(verify_jwt)
    ):
        """
        Upload a markdown file and process it for RAG.
        """
        try:
            # 检查文件类型
            if not file.filename.endswith(".md"):
                raise HTTPException(status_code=400, detail="Only markdown (.md) files are allowed.")

            # 读取文件内容,将文件内容存储为 URL 并保存到用户数据库中
            # 执行后续的 RAG 函数
           
            '''return FileResponse(
                id=uuid4(),
                object="file",
                bytes=len(content),
                created_at=int(time.time()),  # 假设我们使用当前时间戳
                filename=file.filename,
                purpose="user-uploaded-markdown"
            )'''
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading markdown file: {str(e)}")


    @router.post("/files/{file_format}", tags=["files"], response_model=FileResponse)
    async def upload_files(
        file_format: str,
        purpose: str = "user-uploaded-document",
        file: UploadFile = File(...),
        user_id: str = Depends(verify_jwt)
    ):
        """
        Upload a non-markdown file, process it, and store its vector representation.
        """
        try:
            # 确认文件格式是否为允许的格式
            allowed_formats = ["pdf", "docx", "txt",...]  # 假设支持的文件格式
            if file_format not in allowed_formats:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_format}")

            # 读取文件内容
            # 调用 loader 函数处理文件，将文本转化为字符串
            # 将字符串传给 RAG 相关函数进行向量化处理
            # 将向量数据保存到本轮对话的 RAG 部分向量数据库中

            '''return FileResponse(
                id=uuid4(),
                object="file",
                bytes=len(content),
                created_at=int(time.time()),  # 假设我们使用当前时间戳
                filename=file.filename,
                purpose="user-uploaded-document"
            )'''
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

    @router.delete("/files/{file_id}", tags=["files"], response_model=DeleteFileResponse)
    def delete_file(file_id: str, user_id: str = Depends(verify_jwt)):
        """
        Delete a specific file
        """
        try:
            #寻找并删除文件

            #if not 找到:
                raise HTTPException(status_code=404, detail="File not found.")
            #return DeleteFileResponse(id=file_id, object="file", deleted=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

    return router
