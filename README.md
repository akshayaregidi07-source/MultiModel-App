# Multi-Model Comparison Tool

Ask one question to four LLMs through a single [OpenRouter](https://openrouter.ai)
key and compare each answer by **response time** and **cost** — in the terminal
or in a Streamlit web app.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenRouter key to .env
#    OPENROUTER_API_KEY=sk-or-...
```

## Run

**Terminal version:**

```bash
python main.py
```

**Web version (Streamlit):**

```bash
python -m streamlit run app.py
```

The web app opens at `http://localhost:8501`.

## Output

For each model you see:

- **Answer** — the response text
- **Latency** — how long the call took (seconds)
- **Tokens** — input and output token counts
- **Cost** — estimated USD based on published per-token prices

If one model fails, the others still return.

## Models used

| Model | Provider |
|---|---|
| `openai/gpt-4o-mini` | OpenAI |
| `qwen/qwen-2.5-7b-instruct` | Alibaba |
| `deepseek/deepseek-chat` | DeepSeek |
| `meta-llama/llama-3.1-8b-instruct` | Meta |

## Project structure

| File | Purpose |
|---|---|
| `spec.md` | The specification, written first |
| `main.py` | Terminal app + the shared `ask()` engine |
| `app.py` | Streamlit web interface |
| `.env` | Your API key (never committed) |
| `requirements.txt` | Dependencies |

> The API key lives only in `.env`, which is listed in `.gitignore` and never pushed.
