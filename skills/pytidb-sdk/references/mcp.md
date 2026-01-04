# MCP server (tidb-mcp-server)

Install with the mcp extra when you need the MCP server:

```bash
pip install "pytidb[mcp]"
```

Run the server:

```bash
tidb-mcp-server
```

Environment variables (dotenv is loaded automatically):
- TIDB_DATABASE_URL (optional, full mysql+pymysql URL)
- TIDB_HOST (default 127.0.0.1)
- TIDB_PORT (default 4000)
- TIDB_USERNAME (default root)
- TIDB_PASSWORD (default empty)
- TIDB_DATABASE (default test)

Do not commit secrets. Use a local .env and keep it out of version control.
