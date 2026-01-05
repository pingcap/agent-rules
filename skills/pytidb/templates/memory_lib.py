import datetime
import os
from typing import Any, Dict, List

import dotenv
from openai import OpenAI

from pytidb import TiDBClient
from pytidb.datatype import TEXT
from pytidb.embeddings import EmbeddingFunction
from pytidb.schema import Column, Field, TableModel

dotenv.load_dotenv()


def init_clients():
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    tidb_client = TiDBClient.connect(
        host=os.getenv("TIDB_HOST"),
        port=int(os.getenv("TIDB_PORT", 4000)),
        username=os.getenv("TIDB_USERNAME"),
        password=os.getenv("TIDB_PASSWORD"),
        database=os.getenv("TIDB_DATABASE", "memory_example"),
        ensure_db=True,
    )
    embedding_fn = EmbeddingFunction(
        model_name="openai/text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    return openai_client, tidb_client, embedding_fn


class Memory:
    def __init__(self, tidb_client: TiDBClient, embedding_fn: EmbeddingFunction, openai_client: OpenAI):
        self.tidb_client = tidb_client
        self.embedding_fn = embedding_fn
        self.openai_client = openai_client

        class MemoryRecord(TableModel):
            __tablename__ = "memories"
            __table_args__ = {"extend_existing": True}

            id: int = Field(default=None, primary_key=True)
            user_id: str
            memory: str = Field(sa_column=Column(TEXT))
            embedding: List[float] = embedding_fn.VectorField(source_field="memory")
            created_at: datetime.datetime = Field(
                default_factory=lambda: datetime.datetime.now(datetime.UTC)
            )

        self.MemoryRecord = MemoryRecord
        self.table = tidb_client.create_table(schema=MemoryRecord, if_exists="skip")

    def add(self, messages: List[Dict[str, Any]], user_id: str = "default_user"):
        prompt = (
            "Extract the key facts from the following conversation. "
            "Only return the facts as a single string.\n\n"
        )
        for m in messages:
            prompt += f"{m['role']}: {m['content']}\n"

        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_FACT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You extract concise user facts."},
                {"role": "user", "content": prompt},
            ],
        )
        facts = (response.choices[0].message.content or "").strip()
        if not facts:
            return

        record = self.MemoryRecord(user_id=user_id, memory=facts)
        self.table.insert(record)

    def search(self, query: str, user_id: str = "default_user", limit: int = 10) -> List[Dict[str, Any]]:
        return (
            self.table.search(query=query, search_type="vector")
            .filter({"user_id": user_id})
            .limit(limit)
            .to_list()
        )

    def get_all(self, user_id: str = "default_user") -> List[Dict[str, Any]]:
        return self.table.query(filters={"user_id": user_id}, order_by={"created_at": "desc"}).to_list()


def chat_with_memories(message: str, memory: Memory, openai_client: OpenAI, user_id: str = "default_user") -> str:
    memories = memory.search(query=message, user_id=user_id, limit=10)
    memories_str = "\n".join(f"- {entry['memory']}" for entry in memories)

    system_prompt = (
        "You are a helpful assistant. Use the provided memories when relevant.\n"
        f"User Memories:\n{memories_str}"
    )

    response = openai_client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
    )
    assistant_response = response.choices[0].message.content or ""

    memory.add(
        [{"role": "user", "content": message}, {"role": "assistant", "content": assistant_response}],
        user_id=user_id,
    )

    return assistant_response
