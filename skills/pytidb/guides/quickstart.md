# Quickstart (connect → table → insert → vector search)

> This guide is a complete walkthrough with its own phases. Follow in order.

## Workflow checklist

- [ ] Confirm TiDB deployment + connection method
- [ ] Create a Python environment and install deps
- [ ] Configure `.env`
- [ ] Validate connection (`scripts/validate_connection.py`)
- [ ] Run the quickstart template

---

## Phase 1: Context detection

1) Confirm TiDB type:
- TiDB Cloud Starter
- TiDB self-managed (incl. `tiup playground`)

2) Confirm how you want to connect:
- **Connection params** (`TIDB_HOST`, `TIDB_PORT`, ...)
- **Connection string** (`DATABASE_URL` / `TIDB_DATABASE_URL`)

## Phase 2: Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pytidb python-dotenv
```

## Phase 3: Environment variables

Create `.env` (example for TiDB Cloud Starter):

```bash
cat > .env <<'EOF'
TIDB_HOST={gateway-region}.prod.aws.tidbcloud.com
TIDB_PORT=4000
TIDB_USERNAME={prefix}.root
TIDB_PASSWORD={password}
TIDB_DATABASE=quickstart_example

# For embeddings (choose one path)
OPENAI_API_KEY={your-openai-api-key}
EOF
```

## Phase 4: Validate connection

```bash
python scripts/validate_connection.py
```

If this fails, use `guides/troubleshooting.md`.

## Phase 5: Run quickstart template

1) Create `quickstart.py` from `templates/quickstart.py`.
2) Run:

```bash
python quickstart.py
```

Expected behavior:
- Connects to TiDB
- Creates a table with an auto-embedded vector field
- Inserts sample rows
- Runs a semantic search query
---

## Next steps

- CRUD/table modeling: start from `templates/crud.py`
- Auto embedding provider selection: `templates/auto_embedding.py`
- More examples: `guides/demos.md`
