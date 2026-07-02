from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.schemas import ChatRequest, ChatResponse
from app.services.chatbot import OLLAMA_CHAT_MODEL, generate_response

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    try:
        response = await run_in_threadpool(generate_response, payload.message)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Quick Chat needs a locally running Ollama with the '{OLLAMA_CHAT_MODEL}' model pulled "
                f"(run `ollama pull {OLLAMA_CHAT_MODEL}`, or set OLLAMA_CHAT_MODEL to a model you already have). "
                f"Details: {e}"
            ),
        ) from e
    return ChatResponse(response=response)
