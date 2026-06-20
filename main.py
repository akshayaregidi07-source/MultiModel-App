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

QUESTION = "Explain the concept of recursion in programming with a simple example."

MODELS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-2.0-flash-001",
    "meta-llama/llama-3.1-8b-instruct",
]

# Price per 1 million tokens (input, output) in USD — check openrouter.ai/models for live rates
PRICES = {
    "openai/gpt-4o-mini":                  (0.15,  0.60),
    "anthropic/claude-haiku-4-5":          (0.80,  4.00),
    "google/gemini-2.0-flash-001":         (0.10,  0.40),
    "meta-llama/llama-3.1-8b-instruct":   (0.055, 0.055),
}

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

def print_results(results: list[dict]) -> None:
    """Print a readable side-by-side comparison of all model results."""
    COL = 72  # answer preview width

    print("\n" + "=" * (COL + 2))
    print(f"  Question: {QUESTION}")
    print("=" * (COL + 2))

    for r in results:
        print(f"\n{'─' * (COL + 2)}")
        if "error" in r:
            print(f"  MODEL : {r['model']}")
            print(f"  ERROR : {r['error']}")
            continue

        # Wrap the answer to COL characters per line with indentation
        words = r["answer"].split()
        lines, line = [], []
        for word in words:
            if sum(len(w) + 1 for w in line) + len(word) > COL:
                lines.append(" ".join(line))
                line = [word]
            else:
                line.append(word)
        if line:
            lines.append(" ".join(line))

        print(f"  MODEL   : {r['model']}")
        print(f"  LATENCY : {r['latency']:.2f}s   |   "
              f"TOKENS: {r['in_tok']} in / {r['out_tok']} out   |   "
              f"COST: ${r['cost']:.6f}")
        print(f"  ANSWER  :")
        for ln in lines[:8]:          # show up to 8 wrapped lines
            print(f"    {ln}")
        if len(lines) > 8:
            print(f"    … ({len(lines) - 8} more lines)")

    print(f"\n{'=' * (COL + 2)}\n")

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
