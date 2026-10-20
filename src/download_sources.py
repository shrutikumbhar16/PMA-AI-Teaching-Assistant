from pathlib import Path
import time
import yaml
import requests


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "sources.yaml"
RAW_DIR = BASE_DIR / "data" / "raw" / "probabilitycourse"


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


def download_page(source):
    chapter = str(source["chapter"])

    chapter_dir = RAW_DIR / f"chapter{chapter}"
    chapter_dir.mkdir(parents=True, exist_ok=True)

    output_path = chapter_dir / safe_filename(source)

    if output_path.exists():
        print(f"[SKIP] {source['id']} already downloaded")
        return

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(compatible; PMA-AI-Teaching-Assistant/1.0)"
        )
    }

    try:
        response = requests.get(
            source["url"],
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        output_path.write_text(
            response.text,
            encoding="utf-8",
        )

        print(
            f"[OK] {source['id']} - "
            f"{source['title']}"
        )

    except requests.RequestException as e:
        print(
            f"[ERROR] {source['id']} - "
            f"{source['title']}: {e}"
        )


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    sources = load_sources()

    print(
        f"Downloading {len(sources)} "
        "ProbabilityCourse pages...\n"
    )

    for source in sources:
        download_page(source)

        # Avoid sending requests too aggressively
        time.sleep(0.5)

    print("\nDownload complete.")


if __name__ == "__main__":
    main()