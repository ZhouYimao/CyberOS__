from fastapi import APIRouter,HTTPException

router = APIRouter()

def setup_threads_index_router():
    @router.get("/threads/{THREAD_ID}", tags=["threads"]) #response_model待确认
    def get_threads():
        ...

    @router.post("/threads", tags=["threads"]) #response_model待确认
    def create_threads():
        ...
    
    @router.delete("/threads/{THREAD_ID}", tags=["threads"]) #response_model待确认
    def delete_threads():
        ...

    return router