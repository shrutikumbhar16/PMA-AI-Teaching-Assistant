from pathlib import Path
import json
import yaml
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw" / "probabilitycourse"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CONFIG_PATH = BASE_DIR / "config" / "sources.yaml"


def load_sources():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config["sources"]


def safe_filename(source):
    source_id = source["id"].replace(".", "_")

    title = (
        source["title"]
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )

    return f"{source_id}_{title}.html"


def clean_html(html):
    soup = BeautifulSoup(html, "lxml")

    # Remove HTML elements that are never useful for course content
    for tag in soup(
        [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript",
            "iframe",
        ]
    ):
        tag.decompose()

    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id="content")
        or soup.body
    )

    if main_content is None:
        return ""

    text = main_content.get_text(
        separator="\n",
        strip=True,
    )

    lines = []

    noise_lines = {
        "←",
        "→",
        "previous",
        "next",
        "Video Available",
        "Amazon",
    }

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line in noise_lines:
            continue

        # Remove known ProbabilityCourse footer/promotional text
        if line.startswith(
            "The print version of the book is available"
        ):
            continue

        if line.startswith("Practical uncertainty:"):
            continue

        if line.startswith(
            "Useful Ideas in Decision-Making"
        ):
            continue

        lines.append(line)

    return "\n".join(lines)


def process_source(source):
    chapter = str(source["chapter"])

    raw_path = (
        RAW_DIR
        / f"chapter{chapter}"
        / safe_filename(source)
    )

    if not raw_path.exists():
        print(
            f"[MISSING] {source['id']} "
            f"{raw_path}"
        )
        return

    html = raw_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    cleaned_text = clean_html(html)

    document = {
        "id": source["id"],
        "title": source["title"],
        "chapter": source["chapter"],
        "topic": source["topic"],
        "content_type": source.get(
            "content_type",
            "theory",
        ),
        "source": "ProbabilityCourse",
        "source_url": source["url"],
        "text": cleaned_text,
    }

    chapter_dir = (
        PROCESSED_DIR
        / f"chapter{chapter}"
    )

    chapter_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        chapter_dir
        / f"{source['id'].replace('.', '_')}.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            document,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"[OK] {source['id']} - "
        f"{source['title']}"
    )


def main():
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    sources = load_sources()

    print(
        f"Processing {len(sources)} documents...\n"
    )

    for source in sources:
        process_source(source)

    print("\nProcessing complete.")


if __name__ == "__main__":
    main()