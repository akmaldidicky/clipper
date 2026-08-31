# ============================================================
# 🔥 CLIPPER MACHINE — ONE CLICK
#
# YouTube URL
#      ↓
# youtube_run.py
#      ↓
# final.py
#      ↓
# YouTube Upload
#
# Usage:
#   py one_click.py "YOUTUBE_URL"
# ============================================================

import subprocess
import sys
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

YOUTUBE_RUNNER = (
    BASE_DIR /
    "youtube_run.py"
)

FINAL_RUNNER = (
    BASE_DIR /
    "final.py"
)


# ============================================================
# COLORS
# ============================================================

RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"


# ============================================================
# HELPERS
# ============================================================

def header(text):

    print()
    print("=" * 70)

    print(
        f"{BOLD}{CYAN}"
        f"{text}"
        f"{RESET}"
    )

    print("=" * 70)


def success(text):

    print(
        f"{GREEN}✅ {text}{RESET}"
    )


def error(text):

    print(
        f"{RED}❌ {text}{RESET}"
    )


def info(text):

    print(
        f"{CYAN}ℹ {text}{RESET}"
    )


# ============================================================
# CHECK SCRIPT
# ============================================================

def check_script(path):

    if not path.exists():

        error(
            f"File tidak ditemukan: {path}"
        )

        return False

    return True


# ============================================================
# RUN SCRIPT
# ============================================================

def run_script(
    script,
    args=None
):

    if args is None:

        args = []


    command = [

        sys.executable,

        str(script),

        *args
    ]


    result = subprocess.run(

        command,

        cwd=BASE_DIR
    )


    return (
        result.returncode == 0
    )


# ============================================================
# MAIN
# ============================================================

def main():

    header(
        "🔥 CLIPPER MACHINE — ONE CLICK"
    )


    # --------------------------------------------------------
    # CHECK ARGUMENT
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        error(
            "URL YouTube belum diberikan."
        )

        print()

        print(
            "Usage:"
        )

        print()

        print(
            'py one_click.py '
            '"https://youtu.be/VIDEO_ID"'
        )

        print()

        return 1


    youtube_url = (
        sys.argv[1]
    )


    # --------------------------------------------------------
    # CHECK SCRIPTS
    # --------------------------------------------------------

    header(
        "🔍 CHECK PIPELINE"
    )


    if not check_script(
        YOUTUBE_RUNNER
    ):

        return 1


    if not check_script(
        FINAL_RUNNER
    ):

        return 1


    success(
        "youtube_run.py ditemukan"
    )

    success(
        "final.py ditemukan"
    )


    # ========================================================
    # STEP 1
    # ========================================================

    header(
        "🎬 STEP 1 — DOWNLOAD & CLIP"
    )


    info(
        f"Source:"
    )

    print(
        youtube_url
    )

    print()


    if not run_script(

        YOUTUBE_RUNNER,

        [
            youtube_url
        ]

    ):

        error(
            "youtube_run.py gagal."
        )

        error(
            "Pipeline dihentikan."
        )

        return 1


    success(
        "Clipper Machine selesai."
    )


    # ========================================================
    # STEP 2
    # ========================================================

    header(
        "🚀 STEP 2 — FINALIZE & YOUTUBE"
    )


    if not run_script(
        FINAL_RUNNER
    ):

        error(
            "final.py gagal."
        )

        error(
            "Pipeline dihentikan."
        )

        return 1


    # ========================================================
    # COMPLETE
    # ========================================================

    header(
        "🎉 ONE CLICK SELESAI"
    )


    print()

    success(
        "Video berhasil diproses."
    )

    success(
        "Caption berhasil dibuat."
    )

    success(
        "Thumbnail berhasil dibuat."
    )

    success(
        "Video dikirim ke YouTube."
    )

    print()

    info(
        "Thumbnail tetap upload manual "
        "di YouTube Studio."
    )

    print()

    return 0


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )