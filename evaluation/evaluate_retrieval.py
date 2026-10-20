from pathlib import Path
import json
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "src"))

from rag import retrieve

QUESTIONS_PATH = BASE_DIR / "evaluation" / "questions.json"


TOPIC_ALIASES = {
    "central limit theorem": [
        "central limit theorem",
        "limit theorems"
    ],
    "convergence in probability": [
        "convergence in probability",
        "convergence"
    ]
}


def topic_matches(expected, retrieved):
    expected = expected.lower()
    retrieved = retrieved.lower()

    allowed = TOPIC_ALIASES.get(
        expected,
        [expected]
    )

    return any(
        topic in retrieved or retrieved in topic
        for topic in allowed
    )


def main():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total = 0
    top1_correct = 0
    top3_correct = 0

    print("\nPMA Retrieval Evaluation")
    print("=" * 70)

    for item in questions:

        if item["expected_scope"] != "in_scope":
            continue

        question = item["question"]
        expected_topic = item["expected_topic"]

        results = retrieve(question, k=3)

        topics = [
            metadata["topic"]
            for metadata in results["metadatas"][0]
        ]

        distances = results["distances"][0]

        top1_match = topic_matches(
            expected_topic,
            topics[0]
        )

        top3_match = any(
            topic_matches(expected_topic, topic)
            for topic in topics
        )

        total += 1

        if top1_match:
            top1_correct += 1

        if top3_match:
            top3_correct += 1

        print("\nQuestion:", question)
        print("Expected topic:", expected_topic)

        print(
            "Top-1 topic:",
            topics[0]
        )

        print(
            "Top-1 distance:",
            round(distances[0], 4)
        )

        print(
            "Top-1:",
            "PASS" if top1_match else "FAIL"
        )

        print(
            "Top-3 topics:",
            topics
        )

        print(
            "Top-3:",
            "PASS" if top3_match else "FAIL"
        )

    print("\n" + "=" * 70)

    print(
        f"Top-1 Retrieval Accuracy: "
        f"{top1_correct}/{total} "
        f"({top1_correct / total * 100:.2f}%)"
    )

    print(
        f"Top-3 Retrieval Accuracy: "
        f"{top3_correct}/{total} "
        f"({top3_correct / total * 100:.2f}%)"
    )


if __name__ == "__main__":
    main()