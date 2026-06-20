"""
Multi-Model Comparison Tool
Sends one question to four LLMs via OpenRouter and prints each answer
with its latency and cost so you can compare models side by side.
"""

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# ── Configuration ────────────────────────────────────────────────────────────

load_dotenv()  # reads OPENROUTER_API_KEY from .env into os.environ

QUESTION = "Can someday Human can surpass AI? Support your answer in a line."

MODELS = [
    "openai/gpt-4o-mini",
    "qwen/qwen-2.5-7b-instruct",
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.1-8b-instruct",
]

# Price per 1 million tokens (input, output) in USD — check openrouter.ai/models for live rates
PRICES = {
    "openai/gpt-4o-mini":              (0.15,  0.60),
    "qwen/qwen-2.5-7b-instruct":       (0.07,  0.14),
    "deepseek/deepseek-chat":          (0.14,  0.28),
    "meta-llama/llama-3.1-8b-instruct": (0.055, 0.055),
}

MAX_TOKENS = 512  # cap per call — prevents 402 "not enough credits" errors

TIMEOUT = 30  # seconds per call

# ── Core function ─────────────────────────────────────────────────────────────

def ask(client: OpenAI, question: str, model: str) -> dict:
    """
    Send `question` to `model` via OpenRouter.
    Returns a dict with answer, latency, token counts, and estimated cost.
    Raises an exception on failure (caller handles it).
    """
    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT,
    )

    latency = time.perf_counter() - start

    answer = response.choices[0].message.content or ""
    usage = response.usage
    in_tok = usage.prompt_tokens if usage else 0
    out_tok = usage.completion_tokens if usage else 0

    in_price, out_price = PRICES.get(model, (0, 0))
    cost = (in_tok * in_price + out_tok * out_price) / 1_000_000

    return {
        "model":   model,
        "answer":  answer,
        "latency": latency,
        "in_tok":  in_tok,
        "out_tok": out_tok,
        "cost":    cost,
    }

# ── Output formatting ─────────────────────────────────────────────────────────

# Column widths
W = {"model": 32, "answer": 45, "latency": 10, "tokens": 16, "cost": 12}

def _trunc(text: str, width: int) -> str:
    """Truncate text to width, adding '...' if cut."""
    text = text.replace("\n", " ")
    return text if len(text) <= width else text[: width - 3] + "..."

def _divider() -> str:
    return "+-" + "-+-".join("-" * w for w in W.values()) + "-+"

def print_results(results: list[dict]) -> None:
    """Print results as a 5-column comparison table."""
    print(f"\n  Question: {QUESTION}\n")

    # Header
    print(_divider())
    print("| " + " | ".join(
        h.upper().center(w) for h, w in W.items()
    ) + " |")
    print(_divider())

    for r in results:
        if "error" in r:
            model_col  = _trunc(r["model"],         W["model"])
            answer_col = _trunc(f"ERROR: {r['error']}", W["answer"])
            lat_col    = "—".center(W["latency"])
            tok_col    = "—".center(W["tokens"])
            cost_col   = "—".center(W["cost"])
        else:
            model_col  = _trunc(r["model"],          W["model"])
            answer_col = _trunc(r["answer"],          W["answer"])
            lat_col    = f"{r['latency']:.2f}s".center(W["latency"])
            tok_col    = f"{r['in_tok']}in/{r['out_tok']}out".center(W["tokens"])
            cost_col   = f"${r['cost']:.6f}".center(W["cost"])

        print("| " + " | ".join([
            model_col.ljust(W["model"]),
            answer_col.ljust(W["answer"]),
            lat_col,
            tok_col,
            cost_col,
        ]) + " |")
        print(_divider())

# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or api_key.startswith("sk-or-paste"):
        raise SystemExit("ERROR: Set OPENROUTER_API_KEY in your .env file.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    print(f"\nAsking {len(MODELS)} models… (timeout {TIMEOUT}s each)\n")

    results = []
    for model in MODELS:
        print(f"  querying {model} …", end=" ", flush=True)
        try:
            result = ask(client, QUESTION, model)
            print(f"done ({result['latency']:.1f}s)")
            results.append(result)
        except Exception as exc:
            print(f"FAILED — {exc}")
            results.append({"model": model, "error": str(exc)})

    print_results(results)


if __name__ == "__main__":
    main()
