"""
Embedding + Vector Store (stage 3 of the RAG pipeline — run after chunk.py).

Loads documents/processed/chunks.jsonl (output of the ingestion pipeline),
embeds each chunk's text with all-MiniLM-L6-v2 via sentence-transformers, and
stores the vectors in a persistent ChromaDB collection alongside each
chunk's source metadata (source_id, url, description, chunk_index,
n_tokens), so retrieval results can be attributed back to a document.

The collection is configured for cosine similarity (matching the "Semantic
Search (Cosine Similarity)" stage in the architecture diagram) rather than
Chroma's default L2 distance.
"""

import json
import pathlib

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = pathlib.Path(__file__).parent.parent
CHUNKS_PATH = ROOT / "documents" / "processed" / "chunks.jsonl"
CHROMA_DIR = ROOT / "chroma_db"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "howard_dining"

# Chroma has a max batch size for adds; keep well under it either way.
BATCH_SIZE = 100


def load_chunks(path: pathlib.Path = CHUNKS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_index(chunks: list[dict] | None = None) -> chromadb.api.models.Collection.Collection:
    """Embed every chunk and (re)write the persistent ChromaDB collection."""
    chunks = chunks if chunks is not None else load_chunks()

    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Start clean each run so re-embedding after a chunking change doesn't
    # leave stale vectors behind.
    try:
        client.delete_collection(COLLECTION_NAME)
    except (ValueError, chromadb.errors.NotFoundError):
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embedding_model": EMBEDDING_MODEL},
    )

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        embeddings = model.encode([c["text"] for c in batch], show_progress_bar=False).tolist()
        collection.add(
            ids=[c["chunk_id"] for c in batch],
            documents=[c["text"] for c in batch],
            embeddings=embeddings,
            metadatas=[
                {
                    "source_id": c["source_id"],
                    "url": c["url"],
                    "description": c["description"],
                    "chunk_index": c["chunk_index"],
                    "n_tokens": c["n_tokens"],
                }
                for c in batch
            ],
        )

    return collection


def main():
    chunks = load_chunks()
    collection = build_index(chunks)
    print(f"Embedded {len(chunks)} chunks into ChromaDB collection "
          f"'{COLLECTION_NAME}' at {CHROMA_DIR} (count={collection.count()})")


if __name__ == "__main__":
    main()
