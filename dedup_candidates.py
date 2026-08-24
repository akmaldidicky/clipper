import json
import sys
import re
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

OVERLAP_THRESHOLD = 0.50
SEMANTIC_SIMILARITY_THRESHOLD = 0.70


# ============================================================
# BASIC HELPERS
# ============================================================

def get_start(c):
    return float(
        c.get(
            "start",
            c.get("recommended_start", 0)
        )
    )


def get_end(c):
    return float(
        c.get(
            "end",
            c.get("recommended_end", 0)
        )
    )


def get_score(c):

    try:
        return float(c.get("score", 0))
    except:
        return 0


def get_text(c):

    text = c.get("text")

    if text:
        return text

    return c.get(
        "original_text",
        ""
    )


def normalize(text):

    text = text.lower()

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# TIMESTAMP OVERLAP
# ============================================================

def overlap_ratio(a_start, a_end, b_start, b_end):

    intersection = max(
        0,
        min(a_end, b_end)
        -
        max(a_start, b_start)
    )

    duration_a = a_end - a_start
    duration_b = b_end - b_start

    if duration_a <= 0 or duration_b <= 0:
        return 0

    smaller = min(
        duration_a,
        duration_b
    )

    return intersection / smaller


# ============================================================
# SIMPLE TEXT SIMILARITY
# ============================================================

def word_similarity(a, b):

    a_words = set(
        normalize(a).split()
    )

    b_words = set(
        normalize(b).split()
    )

    if not a_words or not b_words:
        return 0

    intersection = len(
        a_words & b_words
    )

    union = len(
        a_words | b_words
    )

    return intersection / union


# ============================================================
# QWEN SEMANTIC CHECK
# ============================================================

def ask_qwen_similarity(a, b):

    prompt = f"""
Kamu adalah editor video.

Tentukan apakah dua kandidat clip berikut membahas
IDE UTAMA yang sama.

Kandidat A:
{get_text(a)}

Kandidat B:
{get_text(b)}

Jawab JSON saja:

{{
  "same_topic": true,
  "score": 0.0
}}

Aturan:
- score 0 sampai 1
- 1 = ide hampir sama
- 0 = ide benar-benar berbeda
- Jangan menilai kualitas.
- Hanya nilai kesamaan topik/ide.
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0
                }
            },
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        result = json.loads(
            data["response"]
        )

        score = float(
            result.get(
                "score",
                0
            )
        )

        return score

    except Exception as e:

        print(
            f"⚠️ Semantic check error: {e}"
        )

        return 0


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) < 2:

        print(
            "Usage:"
        )

        print(
            "py dedup_candidates.py "
            "analysis\\ai_scored_candidates.json"
        )

        sys.exit(1)

    input_path = sys.argv[1]

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as f:

        candidates = json.load(f)

    print("=" * 60)
    print("🔥 CANDIDATE DEDUP V8")
    print("=" * 60)

    print(
        f"Input : {len(candidates)}"
    )

    # ========================================================
    # SORT SCORE
    # ========================================================

    candidates.sort(
        key=get_score,
        reverse=True
    )

    kept = []

    # ========================================================
    # PROCESS
    # ========================================================

    for i, candidate in enumerate(
        candidates,
        1
    ):

        start = get_start(
            candidate
        )

        end = get_end(
            candidate
        )

        score = get_score(
            candidate
        )

        print(
            f"\n[{i}] "
            f"{start:.1f}s → "
            f"{end:.1f}s "
            f"| score={score}"
        )

        duplicate = False

        for existing in kept:

            existing_start = get_start(
                existing
            )

            existing_end = get_end(
                existing
            )

            # ------------------------------------------------
            # STEP 1
            # TIMESTAMP OVERLAP
            # ------------------------------------------------

            overlap = overlap_ratio(
                start,
                end,
                existing_start,
                existing_end
            )

            if overlap >= OVERLAP_THRESHOLD:

                print(
                    f"   ⚠️ Timestamp overlap "
                    f"{overlap * 100:.0f}%"
                )

                duplicate = True

                print(
                    "   🗑️ DUPLICATE"
                )

                break

            # ------------------------------------------------
            # STEP 2
            # TEXT SIMILARITY
            # ------------------------------------------------

            similarity = word_similarity(
                get_text(candidate),
                get_text(existing)
            )

            print(
                f"   Text similarity: "
                f"{similarity:.2f}"
            )

            if similarity >= 0.60:

                print(
                    "   🤖 Checking semantic similarity..."
                )

                semantic_score = ask_qwen_similarity(
                    candidate,
                    existing
                )

                print(
                    f"   Semantic score: "
                    f"{semantic_score:.2f}"
                )

                if (
                    semantic_score
                    >= SEMANTIC_SIMILARITY_THRESHOLD
                ):

                    duplicate = True

                    print(
                        "   🗑️ SAME TOPIC"
                    )

                    break

        # ====================================================
        # KEEP
        # ====================================================

        if not duplicate:

            kept.append(
                candidate
            )

            print(
                "   ✅ KEEP"
            )

    # ========================================================
    # OUTPUT
    # ========================================================

    output_path = (
        "analysis/unique_candidates.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            kept,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)
    print("✅ DEDUP V8 SELESAI")
    print("=" * 60)

    print(
        f"Before : {len(candidates)}"
    )

    print(
        f"After  : {len(kept)}"
    )

    print(
        f"Removed: "
        f"{len(candidates) - len(kept)}"
    )

    print(
        f"Output : {output_path}"
    )


if __name__ == "__main__":
    main()