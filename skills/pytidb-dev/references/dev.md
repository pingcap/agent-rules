# Dev commands and env notes

## Setup

From repo root:

```bash
pip install uv
uv sync --dev
```

Make targets (preferred when available):

```bash
make install_dev
make lint
make format
make test
make build
```

Equivalent direct commands:

```bash
PYTHONPATH=$PWD uv tool run ruff check
PYTHONPATH=$PWD uv tool run ruff format
PYTHONPATH=$PWD uv run pytest tests --durations=10 -v
```

## Tests and env vars

Tests load `tests/.env` via dotenv. Do not commit real credentials. Create a local `.env` with your own values.

Common variables used by tests and examples:
- TIDB_HOST
- TIDB_PORT
- TIDB_USERNAME
- TIDB_PASSWORD
- TIDB_DATABASE
- OPENAI_API_KEY
- JINA_AI_API_KEY
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

## Optional extras

Install extras when you need them:

```bash
pip install "pytidb[models]"   # embeddings and rerankers
pip install "pytidb[pandas]"   # pandas result conversion
pip install "pytidb[mcp]"      # MCP server
```
