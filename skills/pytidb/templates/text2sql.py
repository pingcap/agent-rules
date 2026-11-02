#!/usr/bin/env python3
"""Interactive Text2SQL demo.

The SQL executed here is generated from free-form user input, so treat it as
untrusted: `is_readonly_sql()` only lets a single read-only statement through,
and the account behind `DATABASE_URL` should be granted SELECT only.
"""
import os
import re

import dotenv
from openai import OpenAI
from pydantic import BaseModel

from pytidb import TiDBClient

dotenv.load_dotenv()


class QuestionSQLResponse(BaseModel):
    question: str
    sql: str
    markdown: str


MAX_RESULT_ROWS = 200

# Only read-only statements may be executed.
ALLOWED_STATEMENTS = frozenset({"select", "with"})

# Rejected as whole words, so identifiers and functions such as `created_at`,
# `update_time` or `dropoff` are not affected.
FORBIDDEN_TOKENS = frozenset(
    {
        "alter",
        "backup",
        "benchmark",
        "call",
        "create",
        "deallocate",
        "delete",
        "do",
        "drop",
        "dumpfile",
        "execute",
        "flush",
        "get_lock",
        "grant",
        "handler",
        "insert",
        "kill",
        "load",
        "load_file",
        "lock",
        "merge",
        "outfile",
        "prepare",
        "release_lock",
        "rename",
        "replace",
        "restart",
        "restore",
        "revoke",
        "shutdown",
        "sleep",
        "truncate",
        "unlock",
        "update",
        "upsert",
    }
)

# String literals and quoted identifiers; removed before inspecting SQL syntax.
_LITERAL_OR_IDENTIFIER = re.compile(
    r"""'(?:[^'\\]|\\.|'')*'|"(?:[^"\\]|\\.|"")*"|`(?:[^`]|``)*`""",
    re.DOTALL,
)


def quote_identifier(name: str) -> str:
    """Quote an identifier.

    Identifiers cannot be passed as query parameters, so escape backticks
    instead of interpolating the raw name into SQL.
    """
    if not isinstance(name, str) or not name or len(name) > 64:
        raise ValueError(f"Invalid identifier: {name!r}")
    return f"`{name.replace('`', '``')}`"


def is_readonly_sql(sql: str) -> bool:
    """Return True when `sql` is a single read-only statement.

    This is defense in depth for generated SQL, not a replacement for running
    with a read-only database account.
    """
    if not sql or not sql.strip():
        return False

    # Drop literals and quoted identifiers so only SQL syntax is inspected;
    # a filter value such as 'delete' must not trip the keyword check.
    stripped = _LITERAL_OR_IDENTIFIER.sub(" ", sql).strip()

    # Reject stacked statements and comments (including MySQL executable
    # comments, `/*! ... */`); neither belongs in a single read-only query.
    if ";" in stripped.rstrip(";"):
        return False
    if any(marker in stripped for marker in ("--", "#", "/*", "*/")):
        return False

    tokens = re.findall(r"[a-z_][a-z0-9_]*", stripped.lower())
    if not tokens or tokens[0] not in ALLOWED_STATEMENTS:
        return False

    return not FORBIDDEN_TOKENS.intersection(tokens)


def with_row_limit(sql: str, max_rows: int = MAX_RESULT_ROWS) -> str:
    """Bound the result set so a generated query cannot exhaust memory."""
    statement = sql.strip().rstrip(";").strip()
    if re.search(r"\blimit\b", statement, flags=re.IGNORECASE):
        return statement
    return f"{statement} LIMIT {max_rows}"


def main() -> int:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    database_url = os.getenv("DATABASE_URL")

    if not openai_api_key or not database_url:
        raise SystemExit("Set OPENAI_API_KEY and DATABASE_URL in your environment (.env).")

    db = TiDBClient.connect(database_url=database_url)
    oai = OpenAI(api_key=openai_api_key)

    current_database = db._db_engine.url.database
    table_definitions = []
    for table_name in db.list_tables():
        ddl = db.query(f"SHOW CREATE TABLE {quote_identifier(table_name)}").to_rows()[0]
        table_definitions.append(ddl)

    print("Text2SQL (type 'exit' to quit). Generated SQL is NOT executed by default.")
    while True:
        question = input("\nQuestion> ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue

        parsed = (
            oai.beta.chat.completions.parse(
                model=os.getenv("OPENAI_TEXT2SQL_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior database administrator. "
                            "Write MySQL-compatible SQL to answer the user's question. "
                            "Use backticks for table/column names. "
                            "Return ONLY a single read-only query.\n\n"
                            f"Database: {current_database}\n\n"
                            "Table definitions:\n"
                            + "\n".join("|".join(map(str, t)) for t in table_definitions)
                        ),
                    },
                    {"role": "user", "content": f"Question: {question}\n"},
                ],
                response_format=QuestionSQLResponse,
            )
            .choices[0]
            .message.parsed
        )

        sql = (parsed.sql or "").strip().rstrip(";").strip()
        print("\n--- SQL ---")
        print(sql)

        if not is_readonly_sql(sql):
            print("\nBlocked: generated SQL must be a single read-only statement (SELECT/WITH).")
            continue

        confirm = input("\nExecute this query? [y/N] ").strip().lower()
        if confirm != "y":
            continue

        statement = with_row_limit(sql)
        if statement != sql:
            print(f"\n(Applied LIMIT {MAX_RESULT_ROWS} to bound the result set.)")

        try:
            rows = db.query(statement).to_rows()
            print("\n--- Result (first 20 rows) ---")
            for row in rows[:20]:
                print(row)
            if len(rows) > 20:
                print(f"... ({len(rows)} rows total)")
        except Exception as e:
            print(f"Error executing SQL: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
