from fastapi import APIRouter, HTTPException, Query

from app.schemas import ChatRequest, ChatResponse, TaskCreate, TaskCreateResponse
from app.services.assistant_agent import ask_agent, get_tasks_collection
from app.services.task_storage import get_recent_tasks, store_task

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
async def assistant_chat(payload: ChatRequest):
    try:
        response = await ask_agent(payload.message)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "Personal Assistant needs a locally running Ollama with a tool-calling-capable model "
                "pulled (see OLLAMA_MODEL / README). Details: " + str(e)
            ),
        ) from e
    return ChatResponse(response=response)


@router.post("/tasks", response_model=TaskCreateResponse)
def create_task(payload: TaskCreate):
    collection = get_tasks_collection()
    message = store_task(collection, payload.task, payload.answer, payload.day)
    return TaskCreateResponse(message=message)


@router.get("/tasks/recent", response_model=list[str])
def recent_tasks(limit: int = Query(5, ge=1, le=50)):
    collection = get_tasks_collection()
    return get_recent_tasks(collection, n=limit)
