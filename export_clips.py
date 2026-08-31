# ============================================================
# 🔥 EXPORT CLIPS V8.3
# Final Clips → MP4
# ============================================================

import json
import subprocess
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_VIDEO = Path(
    "input\pidio.mp4"
)

INPUT_CLIPS = Path(
    "analysis/final_clips.json"
)

OUTPUT_DIR = Path(
    "clips"
)


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
# CHECK FFMPEG
# ============================================================

def check_ffmpeg():

    try:

        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return False

        return True

    except FileNotFoundError:

        return False


# ============================================================
# FORMAT TIME
# ============================================================

def format_time(seconds):

    seconds = float(seconds)

    hours = int(
        seconds // 3600
    )

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = seconds % 60

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:06.3f}"
    )


# ============================================================
# EXPORT ONE CLIP
# ============================================================

def export_clip(
    input_video,
    output_file,
    start,
    end
):

    duration = end - start

    command = [

        "ffmpeg",

        "-y",

        "-ss",
        str(start),

        "-i",
        str(input_video),

        "-t",
        str(duration),

        "-map",
        "0:v:0",

        "-map",
        "0:a?",

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-movflags",
        "+faststart",

        str(output_file)

    ]

    print()

    print(
        "🎬 FFmpeg:"
    )

    print(
        f"   Start    : "
        f"{format_time(start)}"
    )

    print(
        f"   End      : "
        f"{format_time(end)}"
    )

    print(
        f"   Duration : "
        f"{duration:.2f}s"
    )

    print()

    result = subprocess.run(
        command
    )

    return result.returncode == 0


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "🔥 EXPORT CLIPS V8.3"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # CHECK VIDEO
    # --------------------------------------------------------

    if not INPUT_VIDEO.exists():

        raise FileNotFoundError(
            f"\nVideo tidak ditemukan:\n"
            f"{INPUT_VIDEO}\n\n"
            f"Edit INPUT_VIDEO di bagian CONFIG."
        )

    # --------------------------------------------------------
    # CHECK FFMPEG
    # --------------------------------------------------------

    print()

    print(
        "🔍 Checking FFmpeg..."
    )

    if not check_ffmpeg():

        raise RuntimeError(
            "\nFFmpeg tidak ditemukan.\n"
            "Pastikan FFmpeg sudah masuk PATH."
        )

    print(
        "✅ FFmpeg OK"
    )

    # --------------------------------------------------------
    # LOAD CLIPS
    # --------------------------------------------------------

    clips = load_json(
        INPUT_CLIPS
    )

    if not isinstance(
        clips,
        list
    ):

        raise ValueError(
            "final_clips.json harus "
            "berupa list."
        )

    print()

    print(
        f"Input video : {INPUT_VIDEO}"
    )

    print(
        f"Clips       : {len(clips)}"
    )

    print(
        f"Output dir  : {OUTPUT_DIR}"
    )

    # --------------------------------------------------------
    # CREATE OUTPUT DIR
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    success = 0
    failed = 0

    for index, clip in enumerate(
        clips,
        1
    ):

        # ----------------------------------------------------
        # Timestamp
        # ----------------------------------------------------

        try:

            start = float(
                clip["start"]
            )

            end = float(
                clip["end"]
            )

        except Exception:

            print()

            print(
                f"❌ CLIP {index}: "
                f"timestamp invalid"
            )

            failed += 1

            continue

        if end <= start:

            print()

            print(
                f"❌ CLIP {index}: "
                f"end <= start"
            )

            failed += 1

            continue

        # ----------------------------------------------------
        # Filename
        # ----------------------------------------------------

        output_file = (
            OUTPUT_DIR
            /
            f"clip_{index:03d}.mp4"
        )

        print()

        print("=" * 60)

        print(
            f"🔥 EXPORTING CLIP {index}"
        )

        print("=" * 60)

        print(
            f"Source : "
            f"{start:.2f}s → "
            f"{end:.2f}s"
        )

        print(
            f"Output : "
            f"{output_file}"
        )

        # ----------------------------------------------------
        # Export
        # ----------------------------------------------------

        ok = export_clip(
            INPUT_VIDEO,
            output_file,
            start,
            end
        )

        if ok:

            success += 1

            print()

            print(
                f"✅ CLIP {index} DONE"
            )

        else:

            failed += 1

            print()

            print(
                f"❌ CLIP {index} FAILED"
            )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()

    print("=" * 60)

    print(
        "🔥 EXPORT SELESAI"
    )

    print("=" * 60)

    print(
        f"Total   : {len(clips)}"
    )

    print(
        f"Success : {success}"
    )

    print(
        f"Failed  : {failed}"
    )

    print()

    print(
        f"Output → {OUTPUT_DIR}\\"
    )

    print()

    # --------------------------------------------------------
    # LIST FILES
    # --------------------------------------------------------

    for file in sorted(
        OUTPUT_DIR.glob(
            "clip_*.mp4"
        )
    ):

        size_mb = (
            file.stat().st_size
            /
            (1024 * 1024)
        )

        print(
            f"🎥 {file.name} "
            f"({size_mb:.2f} MB)"
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()