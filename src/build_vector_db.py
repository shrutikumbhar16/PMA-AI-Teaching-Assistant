from pathlib import Path
import json

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent

CHUNKS_PATH = BASE_DIR / "data" / "chunks" / "pma_chunks.json"
VECTOR_DB_DIR = BASE_DIR / "vector_db"


EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Loading chunks...")
    chunks = load_chunks()

    print(f"Loaded {len(chunks)} chunks.")

    VECTOR_DB_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_DIR)
    )

    # Recreate collection during development
    try:
        client.delete_collection("pma_course")
    except Exception:
        pass

    collection = client.create_collection(
        name="pma_course"
    )

    texts = []
    ids = []
    metadatas = []

    for chunk in chunks:
        texts.append(chunk["text"])
        ids.append(chunk["chunk_id"])

        metadatas.append(
            {
                "document_id": chunk["document_id"],
                "title": chunk["title"],
                "chapter": str(chunk["chapter"]),
                "topic": chunk["topic"],
                "content_type": chunk["content_type"],
                "source": chunk["source"],
                "source_url": chunk["source_url"],
            }
        )

    print("Generating embeddings...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    print("Saving embeddings to ChromaDB...")

    batch_size = 100

    for i in range(0, len(chunks), batch_size):

        collection.add(
            ids=ids[i:i + batch_size],
            documents=texts[i:i + batch_size],
            embeddings=embeddings[
                i:i + batch_size
            ].tolist(),
            metadatas=metadatas[
                i:i + batch_size
            ]
        )

    print("\nVector database created successfully.")
    print(f"Stored chunks: {collection.count()}")
    print(f"Database location: {VECTOR_DB_DIR}")


if __name__ == "__main__":
    main()