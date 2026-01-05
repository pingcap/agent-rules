#!/usr/bin/env python3
import os

import dotenv
from openai import OpenAI
from pydantic import BaseModel

from pytidb import TiDBClient

dotenv.load_dotenv()


class QuestionSQLResponse(BaseModel):
    question: str
    sql: str
    markdown: str


def is_readonly_sql(sql: str) -> bool:
    s = (sql or "").strip().lower()
    if not s:
        return False
    first = s.split(None, 1)[0]
    return first in {"select", "with", "show", "explain", "describe"}


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
        ddl = db.query(f"SHOW CREATE TABLE `{table_name}`").to_rows()[0]
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

        sql = parsed.sql.strip()
        print("\n--- SQL ---")
        print(sql)

        if not is_readonly_sql(sql):
            print("\nBlocked: generated SQL is not read-only.")
            continue

        confirm = input("\nExecute this query? [y/N] ").strip().lower()
        if confirm != "y":
            continue

        try:
            rows = db.query(sql).to_rows()
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
