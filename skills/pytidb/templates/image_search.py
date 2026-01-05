#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import dotenv
from PIL import Image

from pytidb import Table, TiDBClient
from pytidb.embeddings import EmbeddingFunction
from pytidb.schema import DistanceMetric, Field, TableModel

import image_search_data_loader

dotenv.load_dotenv()


def connect_to_tidb() -> TiDBClient:
    return TiDBClient.connect(
        host=os.getenv("TIDB_HOST", "localhost"),
        port=int(os.getenv("TIDB_PORT", "4000")),
        username=os.getenv("TIDB_USERNAME", "root"),
        password=os.getenv("TIDB_PASSWORD", ""),
        database=os.getenv("TIDB_DATABASE", "image_search_example"),
        ensure_db=True,
    )


def setup_embed_fn() -> EmbeddingFunction:
    api_key = os.getenv("JINA_AI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing JINA_AI_API_KEY in environment (.env)")

    return EmbeddingFunction(
        model_name="jina_ai/jina-embedding-v4",
        api_key=api_key,
        timeout=20,
        multimodal=True,
    )


def setup_table(db: TiDBClient, embed_fn: EmbeddingFunction) -> Table:
    class Pet(TableModel):
        __tablename__ = "pets"
        __table_args__ = {"extend_existing": True}

        id: int = Field(primary_key=True)
        breed: str = Field()
        image_uri: str = Field()
        image_name: str = Field()
        image_vec: Optional[List[float]] = embed_fn.VectorField(
            distance_metric=DistanceMetric.L2,
            source_field="image_uri",
            source_type="image",
        )

    return db.create_table(schema=Pet, if_exists="skip")


def search_images(table: Table, query: Any, limit: int) -> List[Dict[str, Any]]:
    results = (
        table.search(query=query)
        .distance_metric(DistanceMetric.L2)
        .limit(limit)
        .to_list()
    )
    for r in results:
        r.pop("image_vec", None)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="PyTiDB image search example (no UI).")
    parser.add_argument("--load-sample", action="store_true", help="Load one image per breed from dataset.")
    parser.add_argument("--load-all", action="store_true", help="Load all images from dataset.")
    parser.add_argument("--dataset-dir", default="oxford_pets/images", help="Path to Oxford Pets images dir.")
    parser.add_argument("--text", help="Text query (text-to-image search).")
    parser.add_argument("--image", help="Image file path (image-to-image search).")
    parser.add_argument("--limit", type=int, default=int(os.getenv("LIMIT", "20")))
    args = parser.parse_args()

    db = connect_to_tidb()
    embed_fn = setup_embed_fn()
    table = setup_table(db, embed_fn)

    if args.load_sample or args.load_all or table.rows() == 0:
        if table.rows() == 0 and not (args.load_sample or args.load_all):
            print("Table is empty. Loading sample data (one per breed).")
            args.load_sample = True

        one_per_breed = True if args.load_sample else False
        print(f"Loading images from {args.dataset_dir} ...")
        ok, total = image_search_data_loader.load_images_to_db(
            table,
            dataset_dir=args.dataset_dir,
            one_per_breed=one_per_breed,
        )
        print(f"Loaded {ok}/{total} images.")

    if args.text and args.image:
        raise SystemExit("Provide only one of --text or --image.")
    if not args.text and not args.image:
        raise SystemExit("Provide --text \"...\" or --image /path/to.jpg")

    query: Any
    if args.text:
        query = args.text
    else:
        query = Image.open(args.image)

    results = search_images(table, query, limit=args.limit)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
