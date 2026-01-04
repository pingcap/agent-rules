# Example catalog

Use each folder's README for exact steps and env variables.

- quickstart: `main.py` (reqs.txt)
- basic: `main.py` (reqs.txt)
- auto_embedding: `main.py` (reqs.txt)
- custom_embedding: `main.py` and `custom_embedding.py` (reqs.txt)
- vector_search: `app.py` (reqs.txt, Streamlit)
- fulltext_search: `app.py` or `example.py` (reqs.txt)
- hybrid_search: `app.py` or `example.py` (reqs.txt)
- image_search: `app.py` + `data_loader.py` (reqs.txt)
- memory: `app.py` (Streamlit) or `main.py` (CLI) (reqs.txt)
- rag: `main.py` (reqs.txt, Streamlit)
- text2sql: `app.py` (reqs.txt, Streamlit)
- vector-search-with-realtime-data: `app.py` (requirements.txt, Streamlit)

Common setup pattern:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r reqs.txt  # or requirements.txt
```

Run pattern:

```bash
python main.py
# or
streamlit run app.py
```
