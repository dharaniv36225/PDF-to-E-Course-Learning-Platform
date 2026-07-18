"""ChromaDB-backed vector store for document chunks."""
from __future__ import annotations

from app.ai.embeddings import get_embedder
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Persistent Chroma collection wrapper keyed per upload."""

    def __init__(self) -> None:
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            import chromadb

            self._client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        return self._client

    @staticmethod
    def collection_name(upload_id: str) -> str:
        return f"doc_{str(upload_id).replace('-', '')}"

    def _collection(self, upload_id: str):
        client = self._ensure_client()
        return client.get_or_create_collection(
            name=self.collection_name(upload_id),
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, upload_id: str, chunks: list[dict]) -> list[str]:
        """Add chunks. Each chunk: {content, chunk_index, page_number}. Returns vector ids."""
        if not chunks:
            return []
        collection = self._collection(upload_id)
        embedder = get_embedder()
        documents = [c["content"] for c in chunks]
        vectors = embedder.embed_documents(documents)
        ids = [f"{upload_id}:{c['chunk_index']}" for c in chunks]
        metadatas = [
            {"chunk_index": c["chunk_index"], "page_number": c.get("page_number") or 0}
            for c in chunks
        ]
        collection.add(ids=ids, documents=documents, embeddings=vectors, metadatas=metadatas)
        logger.info("Added %d chunks to collection for upload %s", len(ids), upload_id)
        return ids

    def query(self, upload_id: str, query_text: str, top_k: int | None = None) -> list[dict]:
        top_k = top_k or settings.RETRIEVER_TOP_K
        collection = self._collection(upload_id)
        embedder = get_embedder()
        query_vector = embedder.embed_query(query_text)
        result = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        dists = (result.get("distances") or [[]])[0]
        results: list[dict] = []
        for doc, meta, dist in zip(docs, metas, dists, strict=False):
            results.append(
                {
                    "content": doc,
                    "chunk_index": meta.get("chunk_index"),
                    "page_number": meta.get("page_number"),
                    "score": round(1.0 - float(dist), 4),
                }
            )
        return results

    def delete_collection(self, upload_id: str) -> None:
        client = self._ensure_client()
        try:
            client.delete_collection(self.collection_name(upload_id))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to delete collection for %s: %s", upload_id, exc)


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
