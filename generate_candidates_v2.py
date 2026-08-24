import sys
import json
from pathlib import Path


MIN_DURATION = 15
MAX_DURATION = 45


def load_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_candidates(segments):
    candidates = []

    n = len(segments)

    for i in range(n):

        start = segments[i]["start"]
        text_parts = []

        for j in range(i, n):

            end = segments[j]["end"]
            duration = end - start

            if duration > MAX_DURATION:
                break

            text_parts.append(segments[j]["text"])

            if duration >= MIN_DURATION:

                candidates.append({
                    "start": start,
                    "end": end,
                    "duration": round(duration, 2),
                    "text": " ".join(text_parts),
                    "segment_start": i,
                    "segment_end": j
                })

    return candidates


def remove_duplicates(candidates):
    """
    Hilangkan kandidat yang terlalu mirip.
    """

    result = []

    for candidate in candidates:

        duplicate = False

        for existing in result:

            start_diff = abs(
                candidate["start"] - existing["start"]
            )

            end_diff = abs(
                candidate["end"] - existing["end"]
            )

            if start_diff < 3 and end_diff < 3:
                duplicate = True
                break

        if not duplicate:
            result.append(candidate)

    return result


def main():

    if len(sys.argv) < 2:
        print(
            "Usage: py generate_candidates_v2.py "
            "analysis\\transcript.json"
        )
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"❌ File tidak ditemukan: {input_file}")
        sys.exit(1)

    segments = load_transcript(input_file)

    print(f"\n🎬 Transcript segments: {len(segments)}")

    candidates = build_candidates(segments)

    print(f"🧠 Raw candidates: {len(candidates)}")

    candidates = remove_duplicates(candidates)

    print(f"✂️ After deduplication: {len(candidates)}")

    output_dir = Path("analysis")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "candidates_v2.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            candidates,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"\n✓ Candidates generated")
    print(f"✓ Output: {output_file}")

    print("\nPreview:\n")

    for i, candidate in enumerate(candidates[:15], 1):

        print(
            f"[{i}] "
            f"{candidate['start']:.1f}s → "
            f"{candidate['end']:.1f}s "
            f"({candidate['duration']:.1f}s)"
        )

        print(
            f"    {candidate['text'][:150]}..."
        )


if __name__ == "__main__":
    main()