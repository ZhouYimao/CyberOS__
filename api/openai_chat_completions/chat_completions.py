from fastapi import APIRouter,HTTPException

router = APIRouter()

def setup_openai_chat_completions_router():
    @router.post("/chat/completions", tags=["chat_completions"]) #response_model待确认
    async def create_chat_completion():
        ...



    return router