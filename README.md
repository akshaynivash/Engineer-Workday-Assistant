# Engineer's Workday Assistant

Three tools at one workbench, none of them the "main" feature: **part sourcing** (tiered relaxation matching for alternative electronic parts), **quick chat** (casual conversation via a local model), and **workday help** (a tool-calling agent for schedule, meal planning, and study Q&A). An async FastAPI backend holds all the real logic; a React/Vite/TypeScript frontend talks to it over HTTP.

[![CI](https://github.com/akshaynivash/Alternative-Part-Finder-Chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/akshaynivash/Alternative-Part-Finder-Chatbot/actions/workflows/ci.yml)
[![Backend CI](https://github.com/akshaynivash/Alternative-Part-Finder-Chatbot/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/akshaynivash/Alternative-Part-Finder-Chatbot/actions/workflows/backend-ci.yml)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)

![Demo](docs/demo.gif)

A ~21s promo (also available as [`docs/demo.mp4`](docs/demo.mp4) for higher quality). See [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md#demo-video) for what it actually is — a Remotion-authored recreation of the app's screens, not a screen capture — plus architecture diagrams and the reasoning behind the non-obvious decisions.

## Features

- **Part Sourcing** — enter a part ID, get ranked alternatives via a 5-tier relaxation algorithm (exact match → progressively relaxed current/breaking-capacity/mounting/fuse-type constraints), with a browse/search panel for when you don't know which ID to try. Explanations are rule-based by default, with an optional AI-generated mode (Phi-1.5).
- **Quick Chat** — general conversation via a locally running Ollama model. No cloud API key, nothing leaves your machine.
- **Workday Help** — a LangChain tool-calling agent routes chat to the right capability (study assistant over a local FAISS index, daily schedule lookup, weekly meal planning) instead of matching on hardcoded keywords, plus a daily task check-in tracker backed by ChromaDB.
- **Independent graceful degradation** — every optional dependency (Ollama, Phi-1.5 weights) fails on its own and explains itself with a specific fix, instead of crashing the app or leaving you guessing. Part Sourcing works with zero local models installed.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React 18 + Vite + TypeScript + Tailwind + shadcn/ui |
| Backend | FastAPI (async), Pydantic, `uv`-managed |
| Matching engine | pandas, tiered constraint relaxation |
| Chat / agent | LangChain (`create_agent`) over a locally running Ollama model |
| Retrieval | Local FAISS index (study material), ChromaDB (tasks + schedule) |
| Tests / lint | pytest + ruff (backend), ESLint (frontend) |

## Setup

Requires Python 3.11+ (with [`uv`](https://docs.astral.sh/uv/)) and Node 18+.

```sh
cd backend && uv sync
cd ../frontend && npm install
```

### Download the local model (optional — only needed for AI-mode Part Sourcing explanations)

```sh
cd task-3
python model_install.py
```

This downloads `microsoft/phi-1.5` into `models/phi-1.5`.

### Quick Chat (optional)

Needs a locally running Ollama with any chat model pulled (defaults to
`mistral`; override via `OLLAMA_CHAT_MODEL`):

```sh
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral
```

### Workday Help (optional)

Needs a locally running Ollama with a **tool-calling-capable** model (plain
`llama2` predates Ollama's tool-calling support and won't work reliably).
Defaults to `mistral`, which supports tool-calling and is small enough to
already be on hand; for more reliable tool adherence, use a model built
specifically for it instead:

```sh
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral   # or set OLLAMA_MODEL to llama3.1 / qwen2.5 for more reliable tool routing
```

No cloud account needed — the study-assistant RAG tool uses a local FAISS
index (`backend/app/services/vectorstore.py`), built automatically from PDFs
in `data/pdfs/` (falling back to `Report.pdf`, which already ships in this
repo) the first time it's used.

## Run

Two processes:

```sh
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev   # http://localhost:5173
```

Copy `frontend/.env.example` to `frontend/.env` (and `backend/.env.example`
to `backend/.env`) to override the defaults if needed.

## Data

`data/Partscleaned.csv` is a **synthetic** fuse catalog (see
`scripts/generate_synthetic_dataset.py`) — no public dataset matches this
schema, so one was generated with plausible real-world rating values to make
the app actually runnable.

## Tests

```sh
cd backend && uv run ruff check . && uv run pytest
cd frontend && npm run lint && npm run build
```

Backend tests cover the matching engine, ChromaDB-backed storage, and the API
layer (HTTP status codes, validation) — all run without any external services
or credentials. CI is split by path: `.github/workflows/backend-ci.yml` runs
on `backend/**` changes, `.github/workflows/ci.yml` runs on everything else.

## More

See [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md) for architecture diagrams (system overview, the tiered-relaxation matching flow, the agent's tool-routing flow), the data model, and more detail on the graceful-degradation design.
