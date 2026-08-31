import json
import re
import sys
from difflib import SequenceMatcher


MIN_DURATION = 15
MAX_DURATION = 45

TEXT_SIMILARITY = 0.80
OVERLAP_THRESHOLD = 0.50


def normalize(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def similarity(a, b):

    a = normalize(a)
    b = normalize(b)

    if not a or not b:
        return 0

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def build_transcript(transcript):

    result = []

    for item in transcript:

        start = float(
            item.get(
                "start",
                0
            )
        )

        end = float(
            item.get(
                "end",
                0
            )
        )

        text = item.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        result.append({
            "start": start,
            "end": end,
            "text": text
        })

    return result


def get_text_in_range(
    segments,
    start,
    end
):

    parts = []

    for seg in segments:

        if (
            seg["end"] > start
            and
            seg["start"] < end
        ):

            parts.append(
                seg["text"]
            )

    return " ".join(parts)


def text_exists(
    target,
    source
):

    target = normalize(target)
    source = normalize(source)

    if not target:
        return True

    if target in source:
        return True

    target_words = target.split()
    source_words = source.split()

    if len(target_words) < 3:
        return False

    window = len(target_words)

    for i in range(
        len(source_words)
        - window
        + 1
    ):

        chunk = " ".join(
            source_words[
                i:i + window
            ]
        )

        if (
            similarity(
                target,
                chunk
            )
            >= TEXT_SIMILARITY
        ):

            return True

    return False


def overlap(
    a_start,
    a_end,
    b_start,
    b_end
):

    intersection = max(
        0,
        min(a_end, b_end)
        - max(a_start, b_start)
    )

    union = (
        max(a_end, b_end)
        -
        min(a_start, b_start)
    )

    if union <= 0:
        return 0

    return intersection / union


def get_start(clip):

    return float(
        clip.get(
            "start",
            clip.get(
                "recommended_start",
                0
            )
        )
    )


def get_end(clip):

    return float(
        clip.get(
            "end",
            clip.get(
                "recommended_end",
                0
            )
        )
    )


def main():

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "py validate_clips.py "
            "analysis\\transcript.json "
            "analysis\\unique_candidates.json"
        )

        sys.exit(1)

    transcript_path = sys.argv[1]
    clips_path = sys.argv[2]

    transcript = load_json(
        transcript_path
    )

    clips = load_json(
        clips_path
    )

    segments = build_transcript(
        transcript
    )

    print()
    print("=" * 60)
    print("🔥 CLIP VALIDATOR")
    print("=" * 60)

    valid = []
    rejected = []

    for i, clip in enumerate(
        clips,
        1
    ):

        start = get_start(clip)
        end = get_end(clip)

        duration = end - start

        problems = []

        # ==========================================
        # DURATION
        # ==========================================

        if duration < MIN_DURATION:

            problems.append(
                f"too short: {duration:.1f}s"
            )

        if duration > MAX_DURATION:

            problems.append(
                f"too long: {duration:.1f}s"
            )

        # ==========================================
        # ORIGINAL BOUNDARY
        # ==========================================

        original_start = clip.get(
            "original_start"
        )

        original_end = clip.get(
            "original_end"
        )

        if (
            original_start is not None
            and
            start < float(original_start)
        ):

            problems.append(
                "start outside candidate"
            )

        if (
            original_end is not None
            and
            end > float(original_end)
        ):

            problems.append(
                "end outside candidate"
            )

        # ==========================================
        # TRANSCRIPT
        # ==========================================

        clip_text = get_text_in_range(
            segments,
            start,
            end
        )

        if not clip_text:

            problems.append(
                "no transcript found"
            )

        # ==========================================
        # TEXT VALIDATION
        # ==========================================

        for field in [
            "hook_text",
            "core_text",
            "payoff_text"
        ]:

            text = clip.get(
                field,
                ""
            )

            if not text:
                continue

            if not text_exists(
                text,
                clip_text
            ):

                problems.append(
                    f"{field} not found in transcript"
                )

        # ==========================================
        # RESULT
        # ==========================================

        if problems:

            rejected.append(
                clip
            )

            print()
            print(
                f"❌ [{i}] "
                f"{start:.1f}s → "
                f"{end:.1f}s"
            )

            for problem in problems:

                print(
                    f"   - {problem}"
                )

        else:

            clip["duration"] = round(
                duration,
                2
            )

            valid.append(
                clip
            )

            print()
            print(
                f"✅ [{i}] "
                f"{start:.1f}s → "
                f"{end:.1f}s"
            )

    # ==============================================
    # FINAL DEDUP
    # ==============================================

    print()
    print("=" * 60)
    print("🔥 FINAL DEDUP")
    print("=" * 60)

    final = []

    for clip in valid:

        start = get_start(clip)
        end = get_end(clip)

        duplicate = False

        for existing in final:

            existing_start = get_start(
                existing
            )

            existing_end = get_end(
                existing
            )

            ov = overlap(
                start,
                end,
                existing_start,
                existing_end
            )

            if ov >= OVERLAP_THRESHOLD:

                duplicate = True

                print(
                    f"🗑️ Duplicate "
                    f"{start:.1f}-{end:.1f}"
                    f" → "
                    f"{existing_start:.1f}-"
                    f"{existing_end:.1f}"
                    f" ({ov * 100:.0f}%)"
                )

                break

        if not duplicate:

            final.append(
                clip
            )

    # ==============================================
    # OUTPUT
    # ==============================================

    output = (
        "analysis/final_clips.json"
    )

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 60)
    print("✅ SELESAI")
    print("=" * 60)

    print(
        f"Input        : {len(clips)}"
    )

    print(
        f"Valid        : {len(valid)}"
    )

    print(
        f"Rejected     : {len(rejected)}"
    )

    print(
        f"Final        : {len(final)}"
    )

    print(
        f"Output       : {output}"
    )


if __name__ == "__main__":
    main()