# Alternative Part Finder Chatbot

A Streamlit app that helps find alternative electronic parts (fuses) based on
their specifications, using a tiered relaxation matching algorithm. It also
includes a general chatbot and a personal assistant (chat, study Q&A, meal
planning, daily task tracking) as two more pages of the same app.

## Features

- **Alternative Part Finder** — enter a part ID, get ranked alternatives via a
  5-tier relaxation algorithm (exact match → progressively relaxed current/
  breaking-capacity/mounting/fuse-type constraints). Explanations are
  rule-based by default, with an optional AI-generated mode (Phi-1.5).
- **Chatbot** — general conversation via Blenderbot.
- **Personal Assistant** — a LangChain tool-calling agent routes chat to the
  right capability (study assistant over a local FAISS index, daily schedule
  lookup, weekly meal planning) instead of matching on hardcoded keywords.
  Daily tasks are tracked in ChromaDB.

Each page degrades gracefully and independently if its dependencies aren't
installed/configured — the whole app doesn't crash because one model isn't
downloaded or one service isn't running.

## Setup

Requires Python 3.10+.

```sh
pip install -r requirements.txt
```

### Download the local models (optional — only needed for Chatbot / AI-mode Part Finder explanations)

```sh
cd task-3
python model_install.py
```

This downloads `facebook/blenderbot_small-90M` into `models/model_blenderbot`
and `microsoft/phi-1.5` into `models/phi-1.5`. (Note: `BlenderbotSmallTokenizer`/
`BlenderbotSmallForConditionalGeneration` are for the *small* Blenderbot variant
specifically — `facebook/blenderbot-3B` uses different classes and won't load
here.)

### Personal Assistant (optional)

Needs a locally running Ollama with a **tool-calling-capable** model (plain
`llama2` predates Ollama's tool-calling support and won't work reliably):

```sh
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1   # or set OLLAMA_MODEL to a different tool-calling model
```

No cloud account needed — the study-assistant RAG tool uses a local FAISS
index (`task-3/utils/vectorstore.py`), built automatically from PDFs in
`data/pdfs/` (falling back to `Report.pdf`, which already ships in this repo)
the first time the page is opened.

## Run

```sh
cd task-3
streamlit run app.py
```

Open `http://localhost:8501`.

## Data

`data/Partscleaned.csv` is a **synthetic** fuse catalog (see
`scripts/generate_synthetic_dataset.py`) — no public dataset matches this
schema, so one was generated with plausible real-world rating values to make
the app actually runnable.

## Tests

```sh
python -m pytest tests/ -v
```

Covers the matching engine and ChromaDB-backed storage — both run without any
external services or credentials. CI (`.github/workflows/ci.yml`) runs these
on every push/PR.
