import json
import sys
from pathlib import Path


MIN_DURATION = 20
MAX_DURATION = 60


def load_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text):
    return (
        text.lower()
        .replace(",", "")
        .replace(".", "")
        .replace("!", "")
        .replace("?", "")
    )


def text_similarity(text_a, text_b):
    """
    Simple similarity berdasarkan kata yang sama.
    Belum pakai AI.
    """

    words_a = set(normalize_text(text_a).split())
    words_b = set(normalize_text(text_b).split())

    if not words_a or not words_b:
        return 0

    intersection = words_a & words_b
    union = words_a | words_b

    return len(intersection) / len(union)


def generate_candidates(segments):
    candidates = []

    for i in range(len(segments)):

        start = segments[i]["start"]
        text_parts = []

        for j in range(i, len(segments)):

            end = segments[j]["end"]

            duration = end - start

            if duration > MAX_DURATION:
                break

            text_parts.append(segments[j]["text"])

            if duration >= MIN_DURATION:

                text = " ".join(text_parts)

                candidates.append({
                    "start": start,
                    "end": end,
                    "duration": round(duration, 2),
                    "text": text
                })

    return candidates


def calculate_overlap(a, b):
    overlap_start = max(a["start"], b["start"])
    overlap_end = min(a["end"], b["end"])

    if overlap_end <= overlap_start:
        return 0

    overlap = overlap_end - overlap_start

    duration_a = a["end"] - a["start"]
    duration_b = b["end"] - b["start"]

    smaller_duration = min(duration_a, duration_b)

    return overlap / smaller_duration


def remove_duplicates(candidates, text_threshold=0.65, overlap_threshold=0.70):

    selected = []

    # Kandidat lebih panjang dulu
    candidates = sorted(
        candidates,
        key=lambda x: x["duration"],
        reverse=True
    )

    for candidate in candidates:

        duplicate = False

        for existing in selected:

            text_sim = text_similarity(
                candidate["text"],
                existing["text"]
            )

            overlap = calculate_overlap(
                candidate,
                existing
            )

            if (
                text_sim >= text_threshold
                or overlap >= overlap_threshold
            ):
                duplicate = True
                break

        if not duplicate:
            selected.append(candidate)

    # Balik urutan berdasarkan timestamp
    selected.sort(key=lambda x: x["start"])

    return selected

def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print('py candidate_generator.py "analysis\\transcript.json"')
        sys.exit(1)

    transcript_path = Path(sys.argv[1])

    if not transcript_path.exists():
        print(f"❌ File tidak ditemukan: {transcript_path}")
        sys.exit(1)

    segments = load_transcript(transcript_path)

    print("\n" + "=" * 60)
    print("CLIPPER MACHINE — CANDIDATE GENERATOR")
    print("=" * 60)

    print(f"Transcript segments : {len(segments)}")

    candidates = generate_candidates(segments)

    print(f"Raw candidates      : {len(candidates)}")

    candidates = remove_duplicates(candidates)

    print(f"After deduplication : {len(candidates)}")

    output_path = Path("analysis") / "candidates.json"

    output_path.write_text(
        json.dumps(
            candidates,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(f"\n✓ Output: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()