from __future__ import annotations

from typing import Any, List, Optional

from pytidb.embeddings.base import BaseEmbeddingFunction, EmbeddingSourceType

try:
    from FlagEmbedding import BGEM3FlagModel  # type: ignore
except Exception as e:  # pragma: no cover
    BGEM3FlagModel = None  # type: ignore


class BGEM3EmbeddingFunction(BaseEmbeddingFunction):
    """
    Example custom embedding function using BGE-M3 via FlagEmbedding.

    Replace this with your own model/provider if needed. The important part is implementing
    the BaseEmbeddingFunction methods and returning lists of floats with consistent dimensions.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        use_fp16: bool = True,
        device: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            model_name=model_name,
            dimensions=1024,  # BGE-M3 dense embedding dimension
            use_fp16=use_fp16,
            device=device,
            **kwargs,
        )

        if BGEM3FlagModel is None:
            raise ImportError(
                "FlagEmbedding is not installed. Run: pip install FlagEmbedding"
            )

        self._model = BGEM3FlagModel(
            self.model_name, use_fp16=use_fp16, device=device
        )

    def _encode_text(self, text: str) -> List[float]:
        output = self._model.encode(text, return_dense=True)
        dense_vec = output["dense_vecs"]

        # Handle single-text vs batch outputs.
        try:
            shape_len = len(dense_vec.shape)
        except Exception:
            shape_len = 1

        if shape_len == 1:
            return dense_vec.tolist()
        return dense_vec[0].tolist()

    def get_query_embedding(
        self,
        query: Any,
        source_type: Optional[EmbeddingSourceType] = "text",
        **kwargs,
    ) -> List[float]:
        if source_type != "text":
            raise ValueError(f"Unsupported source_type: {source_type}")
        return self._encode_text(str(query))

    def get_source_embedding(
        self,
        source: Any,
        source_type: Optional[EmbeddingSourceType] = "text",
        **kwargs,
    ) -> List[float]:
        if source_type != "text":
            raise ValueError(f"Unsupported source_type: {source_type}")
        return self._encode_text(str(source))

    def get_source_embeddings(
        self,
        sources: List[Any],
        source_type: Optional[EmbeddingSourceType] = "text",
        **kwargs,
    ) -> List[List[float]]:
        if source_type != "text":
            raise ValueError(f"Unsupported source_type: {source_type}")

        texts = [str(s) for s in sources]
        output = self._model.encode(texts, return_dense=True)
        dense_vecs = output["dense_vecs"]
        return [v.tolist() for v in dense_vecs]
