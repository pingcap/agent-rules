# Troubleshooting

## Connection failures

1) Run `scripts/validate_connection.py` and read the printed host/db/user summary.
2) Check env vars:
- `TIDB_HOST`, `TIDB_PORT`, `TIDB_USERNAME`, `TIDB_PASSWORD`, `TIDB_DATABASE`
- or a single URL (`DATABASE_URL` / `TIDB_DATABASE_URL`)

Common issues:
- Wrong host/port/user
- Password reset needed (TiDB Cloud console)
- TLS required for some TiDB Cloud Starter public endpoints (use the console “Connect” guidance)

## Full-text search errors

Full-text search availability can be restricted by TiDB Cloud offering/region. If index creation or search fails:
- verify your cluster supports full-text search
- try another supported region/cluster type if applicable

## Embedding failures / timeouts

- Confirm the provider/model name and API key (if required).
- If running lots of inserts with auto embedding, reduce concurrency and batch sizes.

## “Table already defined” in interactive environments

Some interactive environments rerun code frequently. Use patterns like:
- `__table_args__ = {"extend_existing": True}`
- `db.open_table(Model)` or `create_table(..., if_exists="skip")`
