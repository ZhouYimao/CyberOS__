from fastapi import APIRouter,HTTPException,File

router = APIRouter()

def setup_uploads_index_router():
    @router.post("/uploads", tags=["uploads"]) #response_model待确认
    def create_upload():
        ...
    
    @router.post("/uploads/{upload_id}/parts", tags=["uploads"]) #response_model待确认
    def send_file_data(file:bytes=File()):
        ...

    @router.post("/uploads/{upload_id}/complete", tags=["uploads"]) #response_model待确认
    def complete_upload():
        ...

    @router.post("/uploads/{upload_id}/cancel", tags=["uploads"]) #response_model待确认
    def cancel_upload():
        ...
    
    return router