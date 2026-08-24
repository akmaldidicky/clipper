# ============================================================
# 🔥 VERTICAL CLIPS V8.4.1
# Full Video + Blurred Background
# No Center Crop
# ============================================================

import subprocess
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_DIR = Path("clips")
OUTPUT_DIR = Path("vertical")

WIDTH = 1080
HEIGHT = 1920


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

        return result.returncode == 0

    except FileNotFoundError:

        return False


# ============================================================
# CONVERT VIDEO
# ============================================================

def convert_vertical(
    input_file,
    output_file
):

    # --------------------------------------------------------
    # Background
    #
    # Video diperbesar memenuhi 1080x1920,
    # lalu diblur.
    # --------------------------------------------------------

    background = (
        "[0:v]"
        "scale=1080:1920:"
        "force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "boxblur=20:10"
        "[bg]"
    )

    # --------------------------------------------------------
    # Foreground
    #
    # Video asli TIDAK dicrop.
    # Lebar maksimal 1080.
    # --------------------------------------------------------

    foreground = (
        "[0:v]"
        "scale=1080:-2:"
        "force_original_aspect_ratio=decrease"
        "[fg]"
    )

    # --------------------------------------------------------
    # Overlay
    #
    # Video asli diletakkan di tengah.
    # --------------------------------------------------------

    overlay = (
        "[bg][fg]"
        "overlay="
        "(W-w)/2:"
        "(H-h)/2"
        "[v]"
    )

    filter_complex = (
        background
        + ";"
        + foreground
        + ";"
        + overlay
    )

    command = [

        "ffmpeg",

        "-y",

        "-i",
        str(input_file),

        "-filter_complex",
        filter_complex,

        "-map",
        "[v]",

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
        "🔥 VERTICAL CLIPS V8.4.1"
    )

    print(
        "Full Video + Blurred Background"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # CHECK FFMPEG
    # --------------------------------------------------------

    print()

    print(
        "🔍 Checking FFmpeg..."
    )

    if not check_ffmpeg():

        raise RuntimeError(
            "FFmpeg tidak ditemukan."
        )

    print(
        "✅ FFmpeg OK"
    )

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    if not INPUT_DIR.exists():

        raise FileNotFoundError(
            f"Folder tidak ditemukan: "
            f"{INPUT_DIR}"
        )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # FIND CLIPS
    # --------------------------------------------------------

    clips = sorted(
        INPUT_DIR.glob(
            "clip_*.mp4"
        )
    )

    if not clips:

        print()

        print(
            "❌ Tidak ada clip ditemukan."
        )

        return

    print()

    print(
        f"Input clips : {len(clips)}"
    )

    print(
        f"Output      : {WIDTH}x{HEIGHT}"
    )

    print(
        "Mode        : Full Video"
    )

    print(
        "Background  : Blur"
    )

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    success = 0
    failed = 0

    for index, input_file in enumerate(
        clips,
        1
    ):

        output_file = (
            OUTPUT_DIR
            /
            f"short_{index:03d}.mp4"
        )

        print()

        print("=" * 60)

        print(
            f"🎬 PROCESSING "
            f"{input_file.name}"
        )

        print(
            f"→ {output_file}"
        )

        print("=" * 60)

        ok = convert_vertical(
            input_file,
            output_file
        )

        if ok:

            success += 1

            print(
                f"✅ DONE"
            )

        else:

            failed += 1

            print(
                f"❌ FAILED"
            )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()

    print("=" * 60)

    print(
        "🔥 VERTICAL CONVERSION SELESAI"
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


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()