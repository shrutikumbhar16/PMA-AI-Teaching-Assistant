from pathlib import Path
import json
import re


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHUNKS_DIR = BASE_DIR / "data" / "chunks"


SECTION_MARKERS = {
    "Definition": "definition",
    "Theorem": "theorem",
    "Example": "example",
    "Problem": "problem",
}


def normalize_text(text):
    """
    Clean unnecessary line breaks while preserving
    mathematical blocks and semantic structure.
    """

    lines = text.splitlines()

    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


def split_into_sections(text):
    """
    Split a document around semantic markers such as
    Definition, Theorem, Example, and Problem.

    Solution stays attached to the Example/Problem
    that comes before it.
    """

    lines = text.splitlines()

    sections = []

    current_lines = []
    current_type = "theory"

    for line in lines:

        stripped = line.strip()

        # Start new section when we encounter
        # Definition / Theorem / Example / Problem
        if stripped in SECTION_MARKERS:

            if current_lines:
                sections.append(
                    {
                        "content_type": current_type,
                        "text": "\n".join(current_lines).strip(),
                    }
                )

            current_type = SECTION_MARKERS[stripped]

            current_lines = [stripped]

        else:
            current_lines.append(line)

    if current_lines:
        sections.append(
            {
                "content_type": current_type,
                "text": "\n".join(current_lines).strip(),
            }
        )

    return sections


def split_long_section(text, max_chars=2500):
    """
    Split unusually long sections while trying
    to preserve paragraph boundaries.
    """

    if len(text) <= max_chars:
        return [text]

    paragraphs = re.split(r"\n(?=[A-Z])", text)

    chunks = []

    current = ""

    for paragraph in paragraphs:

        if len(current) + len(paragraph) <= max_chars:

            if current:
                current += "\n"

            current += paragraph

        else:

            if current:
                chunks.append(current.strip())

            current = paragraph

    if current:
        chunks.append(current.strip())

    return chunks


def process_document(json_path):

    with open(
        json_path,
        "r",
        encoding="utf-8",
    ) as f:
        document = json.load(f)

    text = normalize_text(document["text"])

    sections = split_into_sections(text)

    chunks = []

    chunk_number = 0

    for section in sections:

        section_chunks = split_long_section(
            section["text"]
        )

        for section_text in section_chunks:

            chunk_number += 1

            chunk = {
                "chunk_id": (
                    f"{document['id']}_chunk_{chunk_number}"
                ),
                "document_id": document["id"],
                "title": document["title"],
                "chapter": document["chapter"],
                "topic": document["topic"],
                "content_type": section["content_type"],
                "source": document["source"],
                "source_url": document["source_url"],
                "text": section_text,
            }

            chunks.append(chunk)

    return chunks


def main():

    CHUNKS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_chunks = []

    json_files = list(
        PROCESSED_DIR.rglob("*.json")
    )

    print(
        f"Found {len(json_files)} processed documents.\n"
    )

    for json_path in json_files:

        chunks = process_document(
            json_path
        )

        all_chunks.extend(chunks)

        print(
            f"[OK] {json_path.name}: "
            f"{len(chunks)} chunks"
        )

    output_path = (
        CHUNKS_DIR
        / "pma_chunks.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            all_chunks,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "\nChunking complete."
    )

    print(
        f"Total chunks: {len(all_chunks)}"
    )

    print(
        f"Saved to: {output_path}"
    )


if __name__ == "__main__":
    main()