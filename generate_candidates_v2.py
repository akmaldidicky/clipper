# ============================================================
# 🔥 GENERATE CANDIDATES V4
# 15s → 180s
# Controlled + Diverse Candidate Generation
# ============================================================

import sys
import json
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

MIN_DURATION = 15
MAX_DURATION = 180

TARGET_DURATIONS = [
    20,
    40,
    75,
    120,
]

# ============================================================
# FINAL CANDIDATE LIMIT
# ============================================================

MAX_FINAL_CANDIDATES = 30

# Minimal jarak start antar kandidat yang dipilih.
# Ini membantu supaya kandidat tidak menumpuk
# di bagian yang sama.
MIN_START_DISTANCE = 8


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
# FIND BEST END SEGMENT
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

        if duration > MAX_DURATION:
            break

        if duration < MIN_DURATION:
            continue

        difference = abs(
            duration - target_duration
        )

        if difference < best_difference:

            best_difference = difference
            best_index = j

    return best_index


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
# BUILD RAW CANDIDATES
# ============================================================

def build_candidates(segments):

    candidates = []

    n = len(segments)

    for i in range(n):

        start = float(
            segments[i]["start"]
        )

        used_end_indexes = set()

        for target_duration in TARGET_DURATIONS:

            end_index = find_best_end(
                segments,
                i,
                target_duration
            )

            if end_index is None:
                continue

            if end_index in used_end_indexes:
                continue

            end = float(
                segments[end_index]["end"]
            )

            duration = end - start

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

                "segment_end": end_index,

                # Seberapa dekat kandidat
                # dengan target durasi.
                "target_duration": target_duration,

                "duration_error": round(
                    abs(
                        duration
                        -
                        target_duration
                    ),
                    2
                )

            })

    return candidates


# ============================================================
# REMOVE EXACT DUPLICATES
# ============================================================

def remove_duplicates(candidates):

    result = []

    seen = set()

    for candidate in candidates:

        key = (
            round(candidate["start"], 1),
            round(candidate["end"], 1)
        )

        if key in seen:
            continue

        seen.add(key)

        result.append(candidate)

    return result


# ============================================================
# CALCULATE OVERLAP
# ============================================================

def overlap_ratio(a, b):

    start_a = a["start"]
    end_a = a["end"]

    start_b = b["start"]
    end_b = b["end"]

    intersection = max(
        0,
        min(end_a, end_b)
        -
        max(start_a, start_b)
    )

    duration_a = end_a - start_a
    duration_b = end_b - start_b

    if duration_a <= 0:
        return 0

    if duration_b <= 0:
        return 0

    smaller = min(
        duration_a,
        duration_b
    )

    return intersection / smaller


# ============================================================
# CANDIDATE QUALITY
# ============================================================

def candidate_quality(candidate):

    duration = candidate["duration"]

    target_error = candidate[
        "duration_error"
    ]

    # Kandidat yang dekat target
    # sedikit lebih diprioritaskan.
    duration_score = max(
        0,
        1 -
        (
            target_error
            /
            60
        )
    )

    # Kandidat terlalu panjang
    # sedikit dikurangi prioritasnya.
    if duration >= 120:

        length_bonus = 0.85

    elif duration >= 60:

        length_bonus = 1.0

    elif duration >= 30:

        length_bonus = 1.05

    else:

        length_bonus = 1.0

    return (
        duration_score
        *
        length_bonus
    )


# ============================================================
# SELECT DIVERSE CANDIDATES
# ============================================================

def select_diverse_candidates(
    candidates,
    max_candidates
):

    if not candidates:
        return []

    # --------------------------------------------------------
    # STEP 1
    # Sort berdasarkan kualitas durasi.
    # --------------------------------------------------------

    ranked = sorted(
        candidates,
        key=candidate_quality,
        reverse=True
    )

    selected = []

    # --------------------------------------------------------
    # STEP 2
    # Ambil kandidat dengan coverage
    # sepanjang video.
    # --------------------------------------------------------

    for candidate in ranked:

        if len(selected) >= max_candidates:
            break

        too_close = False

        for existing in selected:

            # Start terlalu dekat
            start_distance = abs(
                candidate["start"]
                -
                existing["start"]
            )

            if (
                start_distance
                <
                MIN_START_DISTANCE
            ):

                too_close = True
                break

            # Kandidat terlalu overlap
            overlap = overlap_ratio(
                candidate,
                existing
            )

            if overlap >= 0.70:

                too_close = True
                break

        if too_close:
            continue

        selected.append(
            candidate
        )

    # --------------------------------------------------------
    # STEP 3
    # Kalau masih kurang dari limit,
    # isi dari kandidat yang belum terpilih.
    # --------------------------------------------------------

    if len(selected) < max_candidates:

        for candidate in ranked:

            if len(selected) >= max_candidates:
                break

            if candidate in selected:
                continue

            selected.append(
                candidate
            )

    return selected


# ============================================================
# SORT FINAL
# ============================================================

def sort_candidates(candidates):

    return sorted(
        candidates,
        key=lambda c: (
            c["start"],
            c["duration"]
        )
    )


# ============================================================
# REMOVE INTERNAL METADATA
# ============================================================

def clean_candidates(candidates):

    cleaned = []

    for candidate in candidates:

        cleaned.append({

            "start": candidate["start"],

            "end": candidate["end"],

            "duration": candidate["duration"],

            "text": candidate["text"],

            "segment_start":
                candidate["segment_start"],

            "segment_end":
                candidate["segment_end"]

        })

    return cleaned


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
            'py generate_candidates_v2.py '
            '"analysis\\transcript.json"'
        )

        sys.exit(1)

    input_file = Path(
        sys.argv[1]
    )

    if not input_file.exists():

        print(
            f"❌ File tidak ditemukan: "
            f"{input_file}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    segments = load_transcript(
        input_file
    )

    print()
    print("=" * 70)
    print(
        "🔥 CLIPPER MACHINE — "
        "CANDIDATE GENERATOR V4"
    )
    print("=" * 70)

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
        f"Final candidate max: "
        f"{MAX_FINAL_CANDIDATES}"
    )

    print(
        f"Min start distance: "
        f"{MIN_START_DISTANCE}s"
    )

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    candidates = build_candidates(
        segments
    )

    print()

    print(
        f"🧠 Raw candidates: "
        f"{len(candidates)}"
    )

    # --------------------------------------------------------
    # EXACT DEDUP
    # --------------------------------------------------------

    candidates = remove_duplicates(
        candidates
    )

    print(
        f"✂️ After exact dedup: "
        f"{len(candidates)}"
    )

    # --------------------------------------------------------
    # DIVERSITY FILTER
    # --------------------------------------------------------

    candidates = select_diverse_candidates(
        candidates,
        MAX_FINAL_CANDIDATES
    )

    print(
        f"🎯 After diversity filter: "
        f"{len(candidates)}"
    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    candidates = sort_candidates(
        candidates
    )

    # --------------------------------------------------------
    # CLEAN METADATA
    # --------------------------------------------------------

    candidates = clean_candidates(
        candidates
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
        "candidates_v2.json"
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
        candidates,
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
            f"    "
            f"{candidate['text'][:150]}..."
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