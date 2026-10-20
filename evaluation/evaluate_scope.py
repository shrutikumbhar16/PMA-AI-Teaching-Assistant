from pathlib import Path
import json
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "src"))

from rag import retrieve, is_in_scope


QUESTIONS_PATH = (
    BASE_DIR
    / "evaluation"
    / "questions.json"
)


def main():

    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        questions = json.load(f)

    correct = 0
    total = len(questions)

    print("\nPMA Scope Evaluation")
    print("=" * 70)

    for item in questions:

        question = item["question"]
        expected = item["expected_scope"]

        results = retrieve(question)

        predicted = (
            "in_scope"
            if is_in_scope(results)
            else "out_of_scope"
        )

        distance = results["distances"][0][0]

        is_correct = predicted == expected

        if is_correct:
            correct += 1

        print("\nQuestion:", question)
        print("Expected:", expected)
        print("Predicted:", predicted)
        print("Distance:", round(distance, 4))
        print(
            "Result:",
            "PASS" if is_correct else "FAIL"
        )

    accuracy = correct / total

    print("\n" + "=" * 70)
    print(
        f"Scope Accuracy: "
        f"{correct}/{total} "
        f"({accuracy * 100:.2f}%)"
    )


if __name__ == "__main__":
    main()