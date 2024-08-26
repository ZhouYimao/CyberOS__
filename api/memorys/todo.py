from fastapi import APIRouter,HTTPException

router = APIRouter()

def setup_memorys_todo_router():
    @router.get("/memorys/todo", tags=["memorys"]) #response_model待确认
    def get_todo_memory():
        ...

    @router.post("/memorys/todo", tags=["memorys"]) #response_model待确认
    def update_todo_memory():
        ...
    
    @router.delete("/memorys/todo", tags=["memorys"]) #response_model待确认
    def delete_todo_memory():
        ...

    return router