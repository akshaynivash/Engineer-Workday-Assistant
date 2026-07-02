import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import assistant, chat, parts
from app.services.assistant_agent import get_schedule_collection
from app.services.schedule_seed import seed_schedule

load_dotenv()

# Idempotent -- safe to run every startup. Only touches ChromaDB (no Ollama
# needed), so the Schedule tool has real data without a manual setup step.
seed_schedule(get_schedule_collection())

app = FastAPI(
    title="Engineer's Workday Assistant API",
    description=(
        "Backend for a general engineering assistant: part sourcing, quick chat, and workday help "
        "(schedule, study material, meal planning, daily tasks) as equal capabilities of one assistant, "
        "not a hierarchy led by any single one of them."
    ),
)

allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(parts.router)
app.include_router(chat.router)
app.include_router(assistant.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
