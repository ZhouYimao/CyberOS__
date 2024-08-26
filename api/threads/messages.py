from fastapi import APIRouter,HTTPException

router = APIRouter()

def setup_threads_messages_router():
    @router.get("/threads/{THREAD_ID}/messages", tags=["threads"]) #response_model待确认
    def get_threads_messages():
        ...

    @router.post("/threads/{THREAD_ID}/messages", tags=["threads"]) #response_model待确认
    def send_messages_to_agent_in_threads():
        ...

    @router.get("/threads/{THREAD_ID}/messages/{MESSAGE_ID}", tags=["threads"]) #response_model待确认
    def retrieve_a_message():
        ...
    
    @router.delete("/threads/{THREAD_ID}/messages{MESSAGE_ID}", tags=["threads"]) #response_model待确认
    def delete_a_message():
        ...

    return router