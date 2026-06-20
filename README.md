# Multi-Model Comparison Tool

Sends one question to four LLMs via [OpenRouter](https://openrouter.ai) and prints
each answer with its latency and estimated cost.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenRouter key to .env
#    Edit .env and replace the placeholder with your real key:
#    OPENROUTER_API_KEY=sk-or-...
```

## Run

```bash
python main.py
```

## Output

For each model you will see:

- **Model name**
- **Latency** — how long the call took in seconds
- **Tokens** — input and output token counts
- **Cost** — estimated USD based on published per-token prices
- **Answer** — the first ~8 lines of the response

## Changing the question

Edit the `QUESTION` variable near the top of `main.py`.

## Models used

| Model | Provider |
|---|---|
| `openai/gpt-4o-mini` | OpenAI |
| `anthropic/claude-haiku-4-5` | Anthropic |
| `google/gemini-2.0-flash-001` | Google |
| `meta-llama/llama-3.1-8b-instruct` | Meta |
