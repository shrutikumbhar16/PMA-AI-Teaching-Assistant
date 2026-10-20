from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = BASE_DIR / "vector_db"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

MAX_DISTANCE = 1.25


model = SentenceTransformer(
    EMBEDDING_MODEL
)

client = chromadb.PersistentClient(
    path=str(VECTOR_DB_DIR)
)

collection = client.get_collection(
    name="pma_course"
)


def check_scope(query, k=3):
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )[0]

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    best_distance = results["distances"][0][0]

    is_in_scope = best_distance <= MAX_DISTANCE

    return {
        "in_scope": is_in_scope,
        "best_distance": best_distance,
        "results": results
    }


if __name__ == "__main__":
    query = input("Enter question: ")

    result = check_scope(query)

    print(
        "\nBest distance:",
        round(result["best_distance"], 4)
    )

    if result["in_scope"]:
        print("IN SCOPE")
    else:
        print("OUT OF SCOPE")