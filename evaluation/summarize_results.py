from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "evaluation"
    / "results"
    / "answer_evaluation.csv"
)

METRICS = [
    "correctness_1_5",
    "groundedness_1_5",
    "relevance_1_5",
    "clarity_1_5",
    "citation_quality_1_5",
]


def main():
    scores = {
        metric: []
        for metric in METRICS
    }

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig"
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            for metric in METRICS:
                value = row[metric].strip()

                if value:
                    scores[metric].append(
                        float(value)
                    )

    print("\nPMA Answer Evaluation Summary")
    print("=" * 60)

    overall_scores = []

    for metric in METRICS:
        values = scores[metric]

        if not values:
            print(
                f"{metric}: No scores entered"
            )
            continue

        average = sum(values) / len(values)

        overall_scores.extend(values)

        pretty_name = (
            metric
            .replace("_1_5", "")
            .replace("_", " ")
            .title()
        )

        print(
            f"{pretty_name}: "
            f"{average:.2f}/5"
        )

    if overall_scores:
        overall = (
            sum(overall_scores)
            / len(overall_scores)
        )

        print("-" * 60)

        print(
            f"Overall Answer Quality: "
            f"{overall:.2f}/5"
        )


if __name__ == "__main__":
    main()