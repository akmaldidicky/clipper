# ============================================================
# 🔥 CLIPPER MACHINE — CANDIDATE GENERATOR V4
# 15s → 180s
#
# Based on original candidate_generator.py
# Controlled candidate generation
# ============================================================

import json
import sys
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

MIN_DURATION = 15
MAX_DURATION = 180

# Target durasi yang ingin direpresentasikan.
#
# Generator TIDAK membuat semua kemungkinan.
# Hanya mengambil kandidat yang mendekati target.
#
TARGET_DURATIONS = [
    15,
    30,
    45,
    60,
    90,
    120,
    150,
    180,
]

# Maksimal kandidat dari satu starting segment.
MAX_CANDIDATES_PER_START = 4


# ============================================================
# LOAD TRANSCRIPT
# ============================================================

def load_transcript(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# TEXT SIMILARITY
# ============================================================

def normalize_text(text):

    return (
        text
        .lower()
        .replace(",", "")
        .replace(".", "")
        .replace("!", "")
        .replace("?", "")
        .replace(":", "")
        .replace(";", "")
    )


def text_similarity(text_a, text_b):

    words_a = set(
        normalize_text(text_a).split()
    )

    words_b = set(
        normalize_text(text_b).split()
    )

    if not words_a or not words_b:

        return 0

    intersection = words_a & words_b
    union = words_a | words_b

    return (
        len(intersection)
        /
        len(union)
    )


# ============================================================
# BUILD TEXT
# ============================================================

def build_text(
    segments,
    start_index,
    end_index
):

    return " ".join(

        segments[i]["text"]

        for i in range(
            start_index,
            end_index + 1
        )

    )


# ============================================================
# FIND BEST END
# ============================================================

def find_best_end(
    segments,
    start_index,
    target_duration
):

    start = float(
        segments[start_index]["start"]
    )

    best_index = None
    best_difference = float("inf")

    for j in range(
        start_index,
        len(segments)
    ):

        end = float(
            segments[j]["end"]
        )

        duration = end - start

        # ----------------------------------------------------
        # Too long
        # ----------------------------------------------------

        if duration > MAX_DURATION:

            break

        # ----------------------------------------------------
        # Too short
        # ----------------------------------------------------

        if duration < MIN_DURATION:

            continue

        difference = abs(
            duration
            -
            target_duration
        )

        if difference < best_difference:

            best_difference = difference
            best_index = j

    return best_index


# ============================================================
# GENERATE CANDIDATES
# ============================================================

def generate_candidates(
    segments
):

    candidates = []

    for i in range(
        len(segments)
    ):

        start = float(
            segments[i]["start"]
        )

        used_end_indexes = set()

        # ----------------------------------------------------
        # Find best candidate for each target duration
        # ----------------------------------------------------

        for target in TARGET_DURATIONS:

            end_index = find_best_end(
                segments,
                i,
                target
            )

            if end_index is None:

                continue

            # Already used by another target.
            if end_index in used_end_indexes:

                continue

            end = float(
                segments[end_index]["end"]
            )

            duration = end - start

            # ------------------------------------------------
            # Safety
            # ------------------------------------------------

            if duration < MIN_DURATION:
                continue

            if duration > MAX_DURATION:
                continue

            used_end_indexes.add(
                end_index
            )

            candidates.append({

                "start": round(
                    start,
                    2
                ),

                "end": round(
                    end,
                    2
                ),

                "duration": round(
                    duration,
                    2
                ),

                "text": build_text(
                    segments,
                    i,
                    end_index
                ),

                "segment_start": i,

                "segment_end": end_index

            })

            # ------------------------------------------------
            # Limit candidates per start
            # ------------------------------------------------

            if (
                len(used_end_indexes)
                >=
                MAX_CANDIDATES_PER_START
            ):

                break

    return candidates


# ============================================================
# TIMESTAMP OVERLAP
# ============================================================

def calculate_overlap(
    a,
    b
):

    overlap_start = max(
        a["start"],
        b["start"]
    )

    overlap_end = min(
        a["end"],
        b["end"]
    )

    if overlap_end <= overlap_start:

        return 0

    overlap = (
        overlap_end
        -
        overlap_start
    )

    duration_a = (
        a["end"]
        -
        a["start"]
    )

    duration_b = (
        b["end"]
        -
        b["start"]
    )

    smaller_duration = min(
        duration_a,
        duration_b
    )

    if smaller_duration <= 0:

        return 0

    return (
        overlap
        /
        smaller_duration
    )


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(
    candidates,
    text_threshold=0.65,
    overlap_threshold=0.70
):

    selected = []

    # --------------------------------------------------------
    # Longer candidates first.
    #
    # This means if:
    #
    # 8s → 48s
    # 8s → 75s
    #
    # overlap heavily, the longer one gets priority.
    # --------------------------------------------------------

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

            # ------------------------------------------------
            # Same content
            # ------------------------------------------------

            if text_sim >= text_threshold:

                duplicate = True
                break

            # ------------------------------------------------
            # Almost same timestamp
            # ------------------------------------------------

            if overlap >= overlap_threshold:

                duplicate = True
                break

        if not duplicate:

            selected.append(
                candidate
            )

    # --------------------------------------------------------
    # Restore chronological order.
    # --------------------------------------------------------

    selected.sort(
        key=lambda x: (
            x["start"],
            x["end"]
        )
    )

    return selected


# ============================================================
# FINAL BASIC FILTER
# ============================================================

def filter_candidates(
    candidates
):

    result = []

    for candidate in candidates:

        duration = float(
            candidate["duration"]
        )

        if duration < MIN_DURATION:
            continue

        if duration > MAX_DURATION:
            continue

        if not candidate.get("text"):
            continue

        result.append(
            candidate
        )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) < 2:

        print()

        print(
            "Usage:"
        )

        print(
            'py candidate_generator.py '
            '"analysis\\transcript.json"'
        )

        sys.exit(1)

    transcript_path = Path(
        sys.argv[1]
    )

    if not transcript_path.exists():

        print(
            f"❌ File tidak ditemukan: "
            f"{transcript_path}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    segments = load_transcript(
        transcript_path
    )

    print()

    print(
        "=" * 70
    )

    print(
        "🔥 CLIPPER MACHINE — "
        "CANDIDATE GENERATOR V4"
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"Transcript segments : "
        f"{len(segments)}"
    )

    print(
        f"Minimum duration   : "
        f"{MIN_DURATION}s"
    )

    print(
        f"Maximum duration   : "
        f"{MAX_DURATION}s"
    )

    print(
        f"Target durations   : "
        f"{TARGET_DURATIONS}"
    )

    print(
        f"Max per start      : "
        f"{MAX_CANDIDATES_PER_START}"
    )

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    candidates = generate_candidates(
        segments
    )

    print()

    print(
        f"🧠 Raw candidates: "
        f"{len(candidates)}"
    )

    # --------------------------------------------------------
    # BASIC FILTER
    # --------------------------------------------------------

    candidates = filter_candidates(
        candidates
    )

    print(
        f"📏 After duration filter: "
        f"{len(candidates)}"
    )

    # --------------------------------------------------------
    # DEDUP
    # --------------------------------------------------------

    candidates = remove_duplicates(
        candidates
    )

    print(
        f"✂️ After deduplication: "
        f"{len(candidates)}"
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output_dir = Path(
        "analysis"
    )

    output_dir.mkdir(
        exist_ok=True
    )

    output_file = (
        output_dir
        /
        "candidates.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            candidates,
            f,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    print()

    print(
        "✓ Candidates generated"
    )

    print(
        f"✓ Output: {output_file}"
    )

    print()

    print(
        "=" * 70
    )

    print(
        "PREVIEW"
    )

    print(
        "=" * 70
    )

    for i, candidate in enumerate(
        candidates[:20],
        1
    ):

        print()

        print(
            f"[{i}] "
            f"{candidate['start']:.1f}s → "
            f"{candidate['end']:.1f}s "
            f"("
            f"{candidate['duration']:.1f}s"
            f")"
        )

        print(
            "    "
            +
            candidate["text"][:150]
            +
            "..."
        )

    print()

    print(
        "=" * 70
    )

    print(
        f"TOTAL CANDIDATES: "
        f"{len(candidates)}"
    )

    print(
        "=" * 70
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()