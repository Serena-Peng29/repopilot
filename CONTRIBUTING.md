# Contributing

Thanks for your interest in RepoPilot.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,openai]'
```

## Checks

Run these before opening a pull request:

```bash
ruff check .
pytest -q
```

## Local Demo

```bash
repopilot demo
repopilot arena examples/eval_cases.jsonl --providers demo
```

## Notes

- Do not commit local run outputs from `.repopilot/`.
- Do not commit API keys, `.env` files, private keys, or local credentials.
- Default tests should not require network access or API keys.
- If a change adds a new provider or sandbox behavior, include a deterministic test path that can run in CI.
