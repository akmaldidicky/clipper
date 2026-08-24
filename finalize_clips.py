# ============================================================
# 🔥 FINALIZE CLIPS V8.2
# Final validation + overlap filter + ranking
# ============================================================

import json
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path("analysis/refined_clips.json")
OUTPUT_FILE = Path("analysis/final_clips.json")

MIN_DURATION = 15
MAX_DURATION = 180

# Kalau dua clip overlap lebih dari 50%,
# salah satunya akan dibuang.
MAX_OVERLAP_RATIO = 0.50


# ============================================================
# LOAD JSON
# ============================================================

def load_json(path):

    if not path.exists():
        raise FileNotFoundError(
            f"File tidak ditemukan: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# OVERLAP CALCULATOR
# ============================================================

def calculate_overlap(a, b):

    start = max(
        a["start"],
        b["start"]
    )

    end = min(
        a["end"],
        b["end"]
    )

    overlap = max(
        0,
        end - start
    )

    return overlap


# ============================================================
# OVERLAP RATIO
# ============================================================

def overlap_ratio(a, b):

    overlap = calculate_overlap(
        a,
        b
    )

    if overlap <= 0:
        return 0

    duration_a = (
        a["end"] - a["start"]
    )

    duration_b = (
        b["end"] - b["start"]
    )

    # Pakai clip yang lebih pendek
    # sebagai basis perbandingan.
    shortest = min(
        duration_a,
        duration_b
    )

    if shortest <= 0:
        return 1

    return overlap / shortest


# ============================================================
# SCORE
# ============================================================

def get_score(clip):

    score = clip.get(
        "score",
        clip.get(
            "total_score",
            0
        )
    )

    try:
        return float(score)

    except:
        return 0


# ============================================================
# VALIDATE CLIP
# ============================================================

def validate_clip(clip):

    try:

        start = float(
            clip["start"]
        )

        end = float(
            clip["end"]
        )

    except:

        return False, "timestamp invalid"

    if end <= start:

        return False, "end <= start"

    duration = end - start

    if duration < MIN_DURATION:

        return False, (
            f"too short ({duration:.1f}s)"
        )

    if duration > MAX_DURATION:

        return False, (
            f"too long ({duration:.1f}s)"
        )

    return True, "ok"


# ============================================================
# REMOVE OVERLAPPING CLIPS
# ============================================================

def remove_overlaps(clips):

    selected = []

    for clip in clips:

        should_keep = True

        for existing in selected:

            ratio = overlap_ratio(
                clip,
                existing
            )

            if ratio >= MAX_OVERLAP_RATIO:

                print()

                print(
                    "⚠️ OVERLAP DETECTED"
                )

                print(
                    f"   Clip A: "
                    f"{existing['start']:.1f}s → "
                    f"{existing['end']:.1f}s"
                )

                print(
                    f"   Clip B: "
                    f"{clip['start']:.1f}s → "
                    f"{clip['end']:.1f}s"
                )

                print(
                    f"   Overlap: "
                    f"{ratio * 100:.1f}%"
                )

                # Karena clips sudah diurutkan
                # berdasarkan score tertinggi,
                # existing otomatis menang.
                print(
                    "   → Keeping higher score clip"
                )

                should_keep = False

                break

        if should_keep:

            selected.append(
                clip
            )

    return selected


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "🔥 FINALIZE CLIPS V8.2"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    clips = load_json(
        INPUT_FILE
    )

    if not isinstance(
        clips,
        list
    ):

        raise ValueError(
            "refined_clips.json harus "
            "berupa list."
        )

    print()

    print(
        f"Input clips : {len(clips)}"
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    valid_clips = []

    print()

    print(
        "🔍 VALIDATING..."
    )

    for i, clip in enumerate(
        clips,
        1
    ):

        valid, reason = validate_clip(
            clip
        )

        if valid:

            valid_clips.append(
                clip
            )

            print(
                f"✅ [{i}] "
                f"{clip['start']:.1f}s → "
                f"{clip['end']:.1f}s"
            )

        else:

            print(
                f"❌ [{i}] "
                f"REJECTED: "
                f"{reason}"
            )

    # --------------------------------------------------------
    # SORT BY SCORE
    # --------------------------------------------------------

    valid_clips.sort(
        key=get_score,
        reverse=True
    )

    print()

    print(
        "📊 SORTED BY SCORE"
    )

    for i, clip in enumerate(
        valid_clips,
        1
    ):

        print(
            f"{i}. "
            f"score={get_score(clip):.1f} "
            f"| "
            f"{clip['start']:.1f}s → "
            f"{clip['end']:.1f}s"
        )

    # --------------------------------------------------------
    # REMOVE OVERLAPS
    # --------------------------------------------------------

    print()

    print(
        "✂️ REMOVING OVERLAPS..."
    )

    final_clips = remove_overlaps(
        valid_clips
    )

    # --------------------------------------------------------
    # FINAL SORT BY START TIME
    # --------------------------------------------------------

    final_clips.sort(
        key=lambda x: x["start"]
    )

    # --------------------------------------------------------
    # ADD CLIP IDs
    # --------------------------------------------------------

    output = []

    for index, clip in enumerate(
        final_clips,
        1
    ):

        new_clip = dict(
            clip
        )

        new_clip["clip_id"] = index

        new_clip["duration"] = round(
            new_clip["end"]
            -
            new_clip["start"],
            2
        )

        output.append(
            new_clip
        )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

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
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()

    print("=" * 60)

    print(
        "🔥 FINALIZE SELESAI"
    )

    print("=" * 60)

    print(
        f"Input      : {len(clips)}"
    )

    print(
        f"Valid      : {len(valid_clips)}"
    )

    print(
        f"Final      : {len(output)}"
    )

    print()

    for clip in output:

        print(
            f"🎬 CLIP {clip['clip_id']}: "
            f"{clip['start']:.1f}s → "
            f"{clip['end']:.1f}s "
            f"({clip['duration']:.1f}s)"
        )

    print()

    print(
        f"Saved → {OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()