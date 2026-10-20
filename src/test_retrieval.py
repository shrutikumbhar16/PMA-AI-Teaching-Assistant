from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = BASE_DIR / "vector_db"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


model = SentenceTransformer(EMBEDDING_MODEL)

client = chromadb.PersistentClient(
    path=str(VECTOR_DB_DIR)
)

collection = client.get_collection(
    name="pma_course"
)


def search(query, k=5):
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    return results


if __name__ == "__main__":
    query = input("Enter your PMA question: ")

    results = search(query)

    print("\nTop retrieved chunks:\n")

    for i in range(len(results["documents"][0])):

        metadata = results["metadatas"][0][i]
        document = results["documents"][0][i]
        distance = results["distances"][0][i]

        print(f"\n--- Result {i + 1} ---")

        print("Topic:", metadata["topic"])
        print("Type:", metadata["content_type"])
        print("Distance:", round(distance, 4))
        print("Source:", metadata["source_url"])

        print("\nText:")
        print(document[:1200])