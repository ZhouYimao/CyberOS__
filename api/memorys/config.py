from fastapi import APIRouter,HTTPException

router = APIRouter()

def setup_memorys_config_router():
    @router.get("/memorys/config", tags=["memorys"]) #response_model待确认
    def get_config_memory():
        ...

    @router.post("/memorys/config", tags=["memorys"]) #response_model待确认
    def update_config_memory():
        ...
    
    @router.delete("/memorys/config", tags=["memorys"]) #response_model待确认
    def delete_config_memory():
        ...

    return router

    