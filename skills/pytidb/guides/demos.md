# Examples

These are runnable `example.py` templates you can use as-is and then customize.

## Workflow checklist

- [ ] Install deps
- [ ] Configure `.env`
- [ ] Validate connection (`scripts/validate_connection.py`)
- [ ] Run the chosen example

---

## Vector search

1) Install deps:

```bash
pip install pytidb python-dotenv
```

2) Run:

```bash
python templates/vector_search.py "HTAP database"
```

## Hybrid search

1) Install deps:

```bash
pip install pytidb python-dotenv
```

2) Set `OPENAI_API_KEY` in `.env`.
3) Run:

```bash
python templates/hybrid_search.py
```

## Image search

1) Install deps:

```bash
pip install pytidb python-dotenv pillow
```

2) Download dataset (Oxford Pets) into `./oxford_pets/images`.
3) Load + search:

```bash
python templates/image_search.py --load-sample --text "fluffy orange cat"
```
