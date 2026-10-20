from pathlib import Path
import csv
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "src"))

from rag import ask


QUESTIONS = [
    {
        "id": 1,
        "question": "What is expectation of a random variable?",
        "category": "Discrete Random Variables"
    },
    {
        "id": 2,
        "question": "What is the difference between a PMF and a PDF?",
        "category": "Random Variable Distributions"
    },
    {
        "id": 3,
        "question": "Explain the exponential distribution and its expected value.",
        "category": "Continuous Random Variables"
    },
    {
        "id": 4,
        "question": "What does it mean for two random variables to be independent?",
        "category": "Joint Distributions"
    },
    {
        "id": 5,
        "question": "What is a moment generating function and why is it useful?",
        "category": "Moment Generating Functions"
    },
    {
        "id": 6,
        "question": "Explain Markov's inequality.",
        "category": "Probability Bounds"
    },
    {
        "id": 7,
        "question": "Explain the Central Limit Theorem.",
        "category": "Limit Theorems"
    },
    {
        "id": 8,
        "question": "What is convergence in probability?",
        "category": "Convergence"
    },
    {
        "id": 9,
        "question": "What is maximum likelihood estimation?",
        "category": "Estimation"
    },
    {
        "id": 10,
        "question": "How do you find the MLE for the parameter of an exponential distribution?",
        "category": "Estimation"
    }
]


OUTPUT_DIR = BASE_DIR / "evaluation" / "results"
OUTPUT_FILE = OUTPUT_DIR / "answer_evaluation.csv"


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    rows = []

    print("\nPMA Answer Quality Evaluation")
    print("=" * 70)

    for item in QUESTIONS:

        print(
            f"\n[{item['id']}/"
            f"{len(QUESTIONS)}] "
            f"{item['question']}"
        )

        result = ask(
            item["question"]
        )

        source_titles = "; ".join(
            source["title"]
            for source in result["sources"]
        )

        source_urls = "; ".join(
            source["url"]
            for source in result["sources"]
        )

        row = {
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "status": result["status"],
            "retrieval_distance": round(
                result["distance"],
                4
            ),
            "answer": result["answer"],
            "sources": source_titles,
            "source_urls": source_urls,

            # Fill these manually later
            "correctness_1_5": "",
            "groundedness_1_5": "",
            "relevance_1_5": "",
            "clarity_1_5": "",
            "citation_quality_1_5": "",
            "comments": ""
        }

        rows.append(row)

        print(
            "Status:",
            result["status"]
        )

        print(
            "Distance:",
            round(
                result["distance"],
                4
            )
        )

    fieldnames = [
        "id",
        "category",
        "question",
        "status",
        "retrieval_distance",
        "answer",
        "sources",
        "source_urls",
        "correctness_1_5",
        "groundedness_1_5",
        "relevance_1_5",
        "clarity_1_5",
        "citation_quality_1_5",
        "comments"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 70)

    print(
        "Evaluation file created:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()