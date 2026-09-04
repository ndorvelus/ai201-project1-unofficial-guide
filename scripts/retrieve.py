"""
Retrieval (stage 4 of the RAG pipeline — run after embed.py has built the
ChromaDB collection).

Embeds a user query with the same all-MiniLM-L6-v2 model used at index time
and runs a cosine-similarity search against the persisted collection,
returning the top-k chunks with their source metadata and similarity score.
"""

import sys

import chromadb
from sentence_transformers import SentenceTransformer

from embed import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL

DEFAULT_TOP_K = 5  # per planning.md's Retrieval Approach

_model = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve_context(query: str, k: int = DEFAULT_TOP_K) -> list[dict]:
    """Return the top-k chunks most similar to `query`.

    Each result is a dict: {text, similarity, source_id, url, description,
    chunk_index}. `similarity` is cosine similarity in [-1, 1] (1 = closest),
    converted from Chroma's cosine *distance* (distance = 1 - similarity).
    """
    collection = _get_collection()
    query_embedding = _get_model().encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append(
            {
                "text": doc,
                "similarity": 1 - distance,
                "source_id": meta["source_id"],
                "url": meta["url"],
                "description": meta["description"],
                "chunk_index": meta["chunk_index"],
            }
        )
    return hits


def main():
    query = " ".join(sys.argv[1:]) or "What meal plans are available to me as a Junior?"
    hits = retrieve_context(query, k=DEFAULT_TOP_K)

    print(f"Query: {query}\n")
    for i, hit in enumerate(hits, 1):
        print(f"[{i}] similarity={hit['similarity']:.3f}  source={hit['source_id']}  url={hit['url']}")
        print(hit["text"][:300].replace("\n", " "))
        print()


if __name__ == "__main__":
    main()
