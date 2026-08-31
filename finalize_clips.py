# ============================================================
# 🔥 FINALIZE CLIPS V1
# AI Scored Candidates → Final Clips
# ============================================================

import json
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

# Minimal score yang boleh masuk final.
MIN_SCORE = 70

# Maksimal jumlah clip final.
MAX_FINAL_CLIPS = 15

# Jika overlap lebih besar dari ini,
# dianggap terlalu mirip secara timestamp.
OVERLAP_THRESHOLD = 0.50


# ============================================================
# HELPERS
# ============================================================

def get_score(candidate):

    try:

        return float(
            candidate
            .get("ai_analysis", {})
            .get("score", 0)
        )

    except:

        return 0


def get_decision(candidate):

    return (
        candidate
        .get("ai_analysis", {})
        .get("decision", "REJECT")
        .upper()
    )


def get_start(candidate):

    analysis = candidate.get(
        "ai_analysis",
        {}
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

    analysis = candidate.get(
        "ai_analysis",
        {}
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

    return (
        candidate
        .get("ai_analysis", {})
        .get("title", "")
    )


def get_idea(candidate):

    return (
        candidate
        .get("ai_analysis", {})
        .get("main_idea", "")
    )


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

    duration_a = a_end - a_start
    duration_b = b_end - b_start

    if duration_a <= 0:
        return 0

    if duration_b <= 0:
        return 0

    smaller_duration = min(
        duration_a,
        duration_b
    )

    return (
        intersection
        /
        smaller_duration
    )


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

    if not isinstance(data, list):

        raise ValueError(
            "ai_scored_candidates.json "
            "harus berupa list."
        )

    return data


# ============================================================
# FILTER
# ============================================================

def filter_candidates(candidates):

    filtered = []

    for candidate in candidates:

        score = get_score(
            candidate
        )

        decision = get_decision(
            candidate
        )

        if decision == "REJECT":
            continue

        if score < MIN_SCORE:
            continue

        start = get_start(
            candidate
        )

        end = get_end(
            candidate
        )

        if end <= start:
            continue

        duration = end - start

        if duration < 15:
            continue

        if duration > 180:
            continue

        filtered.append(
            candidate
        )

    return filtered


# ============================================================
# SORT
# ============================================================

def sort_candidates(candidates):

    return sorted(
        candidates,
        key=lambda c: (
            get_score(c),
            get_end(c) - get_start(c)
        ),
        reverse=True
    )


# ============================================================
# SELECT FINAL
# ============================================================

def select_final(candidates):

    selected = []

    for candidate in candidates:

        start = get_start(
            candidate
        )

        end = get_end(
            candidate
        )

        score = get_score(
            candidate
        )

        title = get_title(
            candidate
        )

        print()

        print(
            f"Checking: "
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

            overlap = overlap_ratio(
                start,
                end,
                existing_start,
                existing_end
            )

            if overlap >= OVERLAP_THRESHOLD:

                print(
                    f"   ⚠️ Overlap "
                    f"{overlap * 100:.0f}%"
                )

                print(
                    "   🗑️ SKIP"
                )

                duplicate = True

                break

        if duplicate:
            continue

        selected.append(
            candidate
        )

        print(
            "   ✅ KEEP"
        )

        print(
            f"   Title: {title}"
        )

        if len(selected) >= MAX_FINAL_CLIPS:

            break

    return selected


# ============================================================
# BUILD OUTPUT
# ============================================================

def build_output(selected):

    final_clips = []

    for index, candidate in enumerate(
        selected,
        1
    ):

        start = get_start(
            candidate
        )

        end = get_end(
            candidate
        )

        analysis = candidate.get(
            "ai_analysis",
            {}
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

def save_output(final_clips):

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
        "🔥 CLIPPER MACHINE — FINALIZER V1"
    )
    print("=" * 70)

    print(
        f"Input  : {INPUT_FILE}"
    )

    print(
        f"Min score : {MIN_SCORE}"
    )

    print(
        f"Max clips : {MAX_FINAL_CLIPS}"
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
            "❌ Tidak ada kandidat "
            "yang memenuhi syarat."
        )

        return

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    sorted_candidates = sort_candidates(
        filtered
    )

    # --------------------------------------------------------
    # SELECT
    # --------------------------------------------------------

    selected = select_final(
        sorted_candidates
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    final_clips = build_output(
        selected
    )

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