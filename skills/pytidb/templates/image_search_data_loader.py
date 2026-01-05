"""
Data loading utilities for the PyTiDB image search example.

This loads image records from the Oxford Pets dataset into TiDB.
Embeddings are generated automatically (multimodal embedding model required).
"""

import random
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple


def extract_breed_from_filename(filename: str) -> str:
    name_parts = filename.rsplit(".", 1)[0].split("_")[:-1]
    return " ".join(name_parts).replace("_", " ").title()


def process_single_image(img_path: Path, table) -> Dict:
    try:
        breed = extract_breed_from_filename(img_path.name)
        image_uri = f"file://{img_path.resolve()}"
        table.insert({"breed": breed, "image_uri": image_uri, "image_name": img_path.name})
        return {"success": True, "filename": img_path.name}
    except Exception as e:
        return {"success": False, "filename": img_path.name, "error": str(e)}


def load_images_to_db(
    table,
    dataset_dir: str = "oxford_pets/images",
    one_per_breed: bool = False,
    workers: int = 5,
) -> Tuple[int, int]:
    """
    Returns: (ok_count, total_count)
    """
    data_dir = Path(dataset_dir)
    if not data_dir.exists():
        raise FileNotFoundError(
            f"Dataset not found: {data_dir} (download Oxford Pets into ./oxford_pets/images)"
        )

    image_files = [p for p in data_dir.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    if not image_files:
        raise FileNotFoundError(f"No images found under {data_dir}")

    if one_per_breed:
        by_breed: Dict[str, List[Path]] = defaultdict(list)
        for p in image_files:
            by_breed[extract_breed_from_filename(p.name)].append(p)
        images_to_process = [random.choice(v) for v in by_breed.values()]
    else:
        images_to_process = image_files

    total = len(images_to_process)
    done = 0
    ok = 0
    lock = threading.Lock()

    def update(filename: str, success: bool, error: str | None):
        nonlocal done, ok
        with lock:
            done += 1
            if success:
                ok += 1
            if done == 1 or done % 50 == 0 or done == total:
                print(f"[{done}/{total}] {filename}")
            if error:
                print(f"  ERROR: {error}")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_single_image, p, table): p for p in images_to_process}
        for fut in as_completed(futures):
            p = futures[fut]
            try:
                res = fut.result()
                update(res["filename"], res["success"], res.get("error"))
            except Exception as e:
                update(p.name, False, str(e))

    return ok, total
