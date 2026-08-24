# ============================================================
# 🔥 FINALIZE CLIPS V2
# AI Scored Candidates → Smart Final Clips
# ============================================================

import json
import requests
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "analysis/ai_scored_candidates.json"
)

OUTPUT_FILE = Path(
    "analysis/final_clips.json"
)

OLLAMA_URL = (
    "http://localhost:11434/api/generate"
)

MODEL = "qwen2.5:3b"

MIN_SCORE = 70

MAX_FINAL_CLIPS = 5

TIMESTAMP_OVERLAP_THRESHOLD = 0.50

SEMANTIC_SIMILARITY_THRESHOLD = 0.75

AI_TIMEOUT = 120


# ============================================================
# HELPERS
# ============================================================

def get_analysis(candidate):

    return candidate.get(
        "ai_analysis",
        {}
    )


def get_score(candidate):

    try:

        return float(
            get_analysis(candidate)
            .get("score", 0)
        )

    except:

        return 0


def get_decision(candidate):

    return (
        get_analysis(candidate)
        .get(
            "decision",
            "REJECT"
        )
        .upper()
    )


def get_start(candidate):

    analysis = get_analysis(
        candidate
    )

    try:

        return float(
            analysis.get(
                "recommended_start",
                candidate.get("start", 0)
            )
        )

    except:

        return float(
            candidate.get("start", 0)
        )


def get_end(candidate):

    analysis = get_analysis(
        candidate
    )

    try:

        return float(
            analysis.get(
                "recommended_end",
                candidate.get("end", 0)
            )
        )

    except:

        return float(
            candidate.get("end", 0)
        )


def get_title(candidate):

    return get_analysis(
        candidate
    ).get(
        "title",
        ""
    )


def get_idea(candidate):

    return get_analysis(
        candidate
    ).get(
        "main_idea",
        ""
    )


def get_text(candidate):

    text = candidate.get(
        "text",
        ""
    )

    return text


# ============================================================
# TIMESTAMP OVERLAP
# ============================================================

def overlap_ratio(
    a_start,
    a_end,
    b_start,
    b_end
):

    intersection = max(
        0,
        min(a_end, b_end)
        -
        max(a_start, b_start)
    )

    duration_a = (
        a_end - a_start
    )

    duration_b = (
        b_end - b_start
    )

    if duration_a <= 0:
        return 0

    if duration_b <= 0:
        return 0

    smaller = min(
        duration_a,
        duration_b
    )

    return (
        intersection
        /
        smaller
    )


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def ask_qwen_similarity(
    candidate_a,
    candidate_b
):

    text_a = get_text(
        candidate_a
    )

    text_b = get_text(
        candidate_b
    )

    prompt = f"""
Kamu adalah editor video Shorts.

Bandingkan dua kandidat clip berikut.

Tentukan apakah keduanya membahas
IDE UTAMA yang sama.

CLIP A:

{text_a}


CLIP B:

{text_b}


PENTING:

- Jangan menilai kualitas.
- Jangan menilai durasi.
- Jangan menilai siapa yang lebih bagus.
- Hanya tentukan apakah topik/ide utama mereka sama.
- Dua clip boleh memakai kata berbeda tetapi tetap
  dianggap sama jika inti pembahasannya sama.
- Jika hanya sedikit berhubungan tetapi memiliki
  inti pembahasan berbeda, anggap berbeda.

Berikan JSON saja:

{{
    "same_topic": false,
    "score": 0.0
}}

Score:

1.0 = hampir pasti ide yang sama
0.8 = sangat mirip
0.6 = cukup berhubungan
0.4 = sedikit berhubungan
0.0 = berbeda

JSON ONLY.
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

            timeout=AI_TIMEOUT
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

        same_topic = bool(
            result.get(
                "same_topic",
                False
            )
        )

        return same_topic, score

    except Exception as e:

        print(
            f"   ⚠️ Semantic check error: "
            f"{e}"
        )

        # Kalau Qwen gagal,
        # jangan membuang kandidat.
        return False, 0


# ============================================================
# LOAD
# ============================================================

def load_candidates():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"\nFile tidak ditemukan:\n"
            f"{INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    if not isinstance(
        data,
        list
    ):

        raise ValueError(
            "Input harus berupa list."
        )

    return data


# ============================================================
# FILTER
# ============================================================

def filter_candidates(
    candidates
):

    result = []

    for candidate in candidates:

        decision = get_decision(
            candidate
        )

        score = get_score(
            candidate
        )

        start = get_start(
            candidate
        )

        end = get_end(
            candidate
        )

        duration = (
            end - start
        )

        if decision == "REJECT":
            continue

        if score < MIN_SCORE:
            continue

        if duration < 15:
            continue

        if duration > 180:
            continue

        if end <= start:
            continue

        result.append(
            candidate
        )

    return result


# ============================================================
# RANKING
# ============================================================

def rank_candidates(
    candidates
):

    """
    Ranking utama berdasarkan AI score.

    Jika score sama, prefer:
    - clip lebih pendek
    - lebih dekat ke 30-60 detik
    """

    def ranking_key(candidate):

        score = get_score(
            candidate
        )

        start = get_start(
            candidate
        )

        end = get_end(
            candidate
        )

        duration = (
            end - start
        )

        # Target ideal sekitar 45 detik.
        duration_penalty = abs(
            duration - 45
        )

        return (
            score,
            -duration_penalty,
            -start
        )

    return sorted(
        candidates,
        key=ranking_key,
        reverse=True
    )


# ============================================================
# SMART SELECTION
# ============================================================

def select_final(
    candidates
):

    selected = []

    for index, candidate in enumerate(
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

        print()

        print(
            f"[CHECK {index}] "
            f"{start:.1f}s → "
            f"{end:.1f}s "
            f"| {end - start:.1f}s "
            f"| score={score:.0f}"
        )

        duplicate = False

        for existing in selected:

            existing_start = get_start(
                existing
            )

            existing_end = get_end(
                existing
            )

            # ------------------------------------------------
            # TIMESTAMP CHECK
            # ------------------------------------------------

            overlap = overlap_ratio(

                start,
                end,

                existing_start,
                existing_end
            )

            print(
                f"   Timestamp overlap: "
                f"{overlap * 100:.0f}%"
            )

            if (
                overlap
                >= TIMESTAMP_OVERLAP_THRESHOLD
            ):

                print(
                    "   🗑️ DUPLICATE "
                    "(timestamp)"
                )

                duplicate = True

                break

            # ------------------------------------------------
            # SEMANTIC CHECK
            # ------------------------------------------------

            print(
                "   🤖 Checking "
                "semantic similarity..."
            )

            same_topic, semantic_score = (
                ask_qwen_similarity(
                    candidate,
                    existing
                )
            )

            print(
                f"   Semantic score: "
                f"{semantic_score:.2f}"
            )

            if (
                same_topic
                and
                semantic_score
                >= SEMANTIC_SIMILARITY_THRESHOLD
            ):

                print(
                    "   🗑️ DUPLICATE "
                    "(same topic)"
                )

                duplicate = True

                break

        # ----------------------------------------------------
        # KEEP
        # ----------------------------------------------------

        if duplicate:

            continue

        selected.append(
            candidate
        )

        print(
            "   ✅ KEEP"
        )

        print(
            f"   Title: "
            f"{get_title(candidate)}"
        )

        if len(selected) >= MAX_FINAL_CLIPS:

            break

    return selected


# ============================================================
# BUILD OUTPUT
# ============================================================

def build_output(
    selected
):

    final_clips = []

    for index, candidate in enumerate(
        selected,
        1
    ):

        analysis = get_analysis(
            candidate
        )

        start = get_start(
            candidate
        )

        end = get_end(
            candidate
        )

        final_clips.append({

            "clip_id": index,

            "start": round(
                start,
                2
            ),

            "end": round(
                end,
                2
            ),

            "duration": round(
                end - start,
                2
            ),

            "score": get_score(
                candidate
            ),

            "decision": get_decision(
                candidate
            ),

            "title": analysis.get(
                "title",
                ""
            ),

            "main_idea": analysis.get(
                "main_idea",
                ""
            ),

            "hook": analysis.get(
                "hook",
                ""
            ),

            "payoff": analysis.get(
                "payoff",
                ""
            ),

            "reason": analysis.get(
                "reason",
                ""
            )

        })

    return final_clips


# ============================================================
# SAVE
# ============================================================

def save_output(
    final_clips
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final_clips,
            f,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print("=" * 70)

    print(
        "🔥 CLIPPER MACHINE — "
        "FINALIZER V2"
    )

    print("=" * 70)

    print(
        f"Input     : "
        f"{INPUT_FILE}"
    )

    print(
        f"Model     : "
        f"{MODEL}"
    )

    print(
        f"Min score : "
        f"{MIN_SCORE}"
    )

    print(
        f"Max clips : "
        f"{MAX_FINAL_CLIPS}"
    )

    print(
        f"Semantic threshold : "
        f"{SEMANTIC_SIMILARITY_THRESHOLD}"
    )

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    candidates = load_candidates()

    print()

    print(
        f"Input candidates : "
        f"{len(candidates)}"
    )

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    filtered = filter_candidates(
        candidates
    )

    print(
        f"After filtering  : "
        f"{len(filtered)}"
    )

    if not filtered:

        print()

        print(
            "❌ Tidak ada candidate "
            "yang memenuhi syarat."
        )

        return

    # --------------------------------------------------------
    # RANK
    # --------------------------------------------------------

    ranked = rank_candidates(
        filtered
    )

    # --------------------------------------------------------
    # SELECT
    # --------------------------------------------------------

    selected = select_final(
        ranked
    )

    # --------------------------------------------------------
    # BUILD
    # --------------------------------------------------------

    final_clips = build_output(
        selected
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    save_output(
        final_clips
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()

    print("=" * 70)

    print(
        "🔥 FINAL CLIPS"
    )

    print("=" * 70)

    for clip in final_clips:

        print()

        print(
            f"#{clip['clip_id']} "
            f"[{clip['score']:.0f}/100]"
        )

        print(
            f"{clip['start']:.1f}s → "
            f"{clip['end']:.1f}s "
            f"({clip['duration']:.1f}s)"
        )

        print(
            f"Title : "
            f"{clip['title']}"
        )

        print(
            f"Idea  : "
            f"{clip['main_idea']}"
        )

    print()

    print("=" * 70)

    print(
        f"Total final clips : "
        f"{len(final_clips)}"
    )

    print(
        f"✓ Output : "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()