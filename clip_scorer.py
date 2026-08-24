import json
import sys
import re
from pathlib import Path


HOOK_WORDS = [
    "kenapa",
    "ternyata",
    "sebenarnya",
    "jangan",
    "ingat",
    "masalahnya",
    "yang paling",
    "tidak semua",
    "satu hal",
]

EMOTION_WORDS = [
    "cinta",
    "bahagia",
    "sedih",
    "takut",
    "sakit",
    "gagal",
    "menang",
    "kehilangan",
    "marah",
    "rindu",
]

WEAK_START_WORDS = [
    "dan",
    "karena",
    "dengan",
    "akan",
    "tapi",
    "jadi",
    "lalu",
]


def calculate_duration_score(duration):

    if 30 <= duration <= 50:
        return 10

    if 20 <= duration < 30:
        return 8

    if 50 < duration <= 60:
        return 8

    return 5


def calculate_hook_score(text):

    text_lower = text.lower()

    score = 0

    for word in HOOK_WORDS:

        if word in text_lower:
            score += 2

    if "?" in text:
        score += 3

    return min(score, 10)


def calculate_emotion_score(text):

    text_lower = text.lower()

    score = 0

    for word in EMOTION_WORDS:

        if word in text_lower:
            score += 1

    return min(score, 10)


def calculate_standalone_score(text):

    words = text.strip().lower().split()

    if not words:
        return 0

    first_word = words[0]

    if first_word in WEAK_START_WORDS:
        return 4

    return 10


def score_candidate(candidate):

    text = candidate["text"]
    duration = candidate["duration"]

    duration_score = calculate_duration_score(duration)
    hook_score = calculate_hook_score(text)
    emotion_score = calculate_emotion_score(text)
    standalone_score = calculate_standalone_score(text)

    total = (
        duration_score
        + hook_score
        + emotion_score
        + standalone_score
    )

    return {
        **candidate,
        "scores": {
            "duration": duration_score,
            "hook": hook_score,
            "emotion": emotion_score,
            "standalone": standalone_score,
        },
        "score": total
    }


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print('py clip_scorer.py "analysis\\candidates.json"')
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"❌ File tidak ditemukan: {input_path}")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    scored = [
        score_candidate(candidate)
        for candidate in candidates
    ]

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    output_path = Path("analysis") / "scored_candidates.json"

    output_path.write_text(
        json.dumps(
            scored,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("CLIPPER MACHINE — CLIP SCORER")
    print("=" * 60)

    for i, clip in enumerate(scored, start=1):

        print(
            f"\n#{i} "
            f"{clip['start']:.1f}s → "
            f"{clip['end']:.1f}s "
            f"| SCORE: {clip['score']}"
        )

        print(
            f"Hook: {clip['scores']['hook']} | "
            f"Emotion: {clip['scores']['emotion']} | "
            f"Standalone: {clip['scores']['standalone']}"
        )

        print(f"Text: {clip['text'][:120]}...")

    print("\n" + "=" * 60)
    print(f"✓ Output: {output_path}")


if __name__ == "__main__":
    main()