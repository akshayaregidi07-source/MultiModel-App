# Spec — Multi-Model Comparison Tool

## Goal
Ask one question to four LLMs via OpenRouter and show each answer
with its speed and cost, so I can compare models for a real task.

## Input
- A single question (string). Hardcoded first; later read from input().

## Output (per model)
- answer text
- latency (seconds)
- tokens (input / output)
- cost (USD)

## Models (OpenRouter IDs)
- openai/gpt-4o-mini
- anthropic/claude-haiku-4-5
- google/gemini-2.0-flash-001
- meta-llama/llama-3.1-8b-instruct

## Pipeline
1. Load OPENROUTER_API_KEY from .env using python-dotenv.
2. For each model: send the question, time the call, read token usage from response.
3. cost = (in_tokens * in_price + out_tokens * out_price) / 1_000_000
4. Print all four results side by side in the terminal.

## Error handling
- Wrap each model call in try/except.
- On failure, log the error and continue with the remaining models.
- Set a per-call timeout so one slow model does not block the rest.

## Done when
- One run shows four answers, each with speed and cost.
- One failing model does not stop the others.
- No API key appears in any source file.
