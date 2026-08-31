# ============================================================
# 🔥 CLIPPER MACHINE - ONE CLICK RUNNER V1
# ============================================================
#
# ONE COMMAND → FULL PIPELINE
#
# INPUT VIDEO
#     ↓
# TRANSCRIBE
#     ↓
# PARSE SRT
#     ↓
# GENERATE CANDIDATES
#     ↓
# REFINE
#     ↓
# FINALIZE
#     ↓
# EXPORT CLIPS
#     ↓
# VERTICAL
#     ↓
# SUBTITLE
#     ↓
# FINAL VIDEO
#
# ============================================================

import subprocess
import sys
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
TRANSCRIPT_DIR = BASE_DIR / "transcripts"
ANALYSIS_DIR = BASE_DIR / "analysis"
CLIPS_DIR = BASE_DIR / "clips"
VERTICAL_DIR = BASE_DIR / "vertical"
SUBTITLED_DIR = BASE_DIR / "subtitled"


# ============================================================
# PIPELINE
# ============================================================

SCRIPTS = [
    ("TRANSCRIBE", "transcribe.py"),
    ("PARSE SRT", "parse_srt.py"),
    ("GENERATE CANDIDATES", "generate_candidates_v2.py"),
    ("REFINE", "refine_clips.py"),
    ("FINALIZE", "finalize_clips.py"),
    ("EXPORT CLIPS", "export_clips.py"),
    ("VERTICAL", "vertical_clips.py"),
    ("SUBTITLE", "subtitle_clips.py"),
]


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
# PRINT HELPERS
# ============================================================

def title(text):

    print()
    print("=" * 70)
    print(
        f"{BOLD}{CYAN}{text}{RESET}"
    )
    print("=" * 70)


def info(text):

    print(
        f"{CYAN}ℹ {text}{RESET}"
    )


def success(text):

    print(
        f"{GREEN}✅ {text}{RESET}"
    )


def warning(text):

    print(
        f"{YELLOW}⚠ {text}{RESET}"
    )


def error(text):

    print(
        f"{RED}❌ {text}{RESET}"
    )


# ============================================================
# FIND INPUT VIDEO
# ============================================================

def find_input_video():

    INPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    extensions = {
        ".mp4",
        ".mov",
        ".mkv",
        ".avi",
        ".webm",
        ".m4v"
    }

    videos = [
        p
        for p in INPUT_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in extensions
    ]

    if not videos:

        return None

    # Video terbaru
    videos.sort(
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    return videos[0]


# ============================================================
# FIND SRT
# ============================================================

def find_srt(video):

    TRANSCRIPT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # PRIORITAS 1
    # Nama SRT sama dengan nama video
    # --------------------------------------------------------

    expected = (
        TRANSCRIPT_DIR
        /
        f"{video.stem}.srt"
    )

    if expected.exists():

        return expected

    # --------------------------------------------------------
    # PRIORITAS 2
    # Cari SRT terbaru
    # --------------------------------------------------------

    srt_files = list(
        TRANSCRIPT_DIR.glob("*.srt")
    )

    if not srt_files:

        return None

    srt_files.sort(
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    return srt_files[0]


# ============================================================
# CHECK REQUIRED SCRIPTS
# ============================================================

def check_required_files():

    missing = []

    for label, script in SCRIPTS:

        path = BASE_DIR / script

        if not path.exists():

            missing.append(
                script
            )

    if missing:

        error(
            "Script berikut tidak ditemukan:"
        )

        for item in missing:

            print(
                f"   - {item}"
            )

        return False

    return True


# ============================================================
# CLEAN OLD OUTPUT
# ============================================================

def clean_old_outputs():

    title(
        "🧹 CLEAN OUTPUT LAMA"
    )

    # --------------------------------------------------------
    # CREATE FOLDERS
    # --------------------------------------------------------

    folders = [
        TRANSCRIPT_DIR,
        ANALYSIS_DIR,
        CLIPS_DIR,
        VERTICAL_DIR,
        SUBTITLED_DIR,
    ]

    for folder in folders:

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    analysis_files = [
        "transcript.json",
        "candidates.json",
        "refined_clips.json",
        "final_clips.json",
    ]

    for filename in analysis_files:

        path = (
            ANALYSIS_DIR
            /
            filename
        )

        if path.exists():

            path.unlink()

            info(
                f"Hapus {path}"
            )

    # --------------------------------------------------------
    # CLIPS
    # --------------------------------------------------------

    for file in CLIPS_DIR.glob(
        "clip_*.mp4"
    ):

        file.unlink()

        info(
            f"Hapus clips/{file.name}"
        )

    # --------------------------------------------------------
    # VERTICAL
    # --------------------------------------------------------

    for file in VERTICAL_DIR.glob(
        "short_*.mp4"
    ):

        file.unlink()

        info(
            f"Hapus vertical/{file.name}"
        )

    # --------------------------------------------------------
    # SUBTITLED
    # --------------------------------------------------------

    for file in SUBTITLED_DIR.glob(
        "final_*.mp4"
    ):

        file.unlink()

        info(
            f"Hapus subtitled/{file.name}"
        )


# ============================================================
# RUN SCRIPT
# ============================================================

def run_script(
    label,
    script,
    video=None
):

    title(
        f"🔥 {label}"
    )

    script_path = (
        BASE_DIR
        /
        script
    )

    info(
        f"Running: {script}"
    )

    command = [
        sys.executable,
        str(script_path)
    ]

    # ========================================================
    # TRANSCRIBE
    # ========================================================

    if script == "transcribe.py":

        if video is None:

            error(
                "Video tidak ditemukan."
            )

            return False

        command.append(
            str(video)
        )

    # ========================================================
    # PARSE SRT
    # ========================================================

    elif script == "parse_srt.py":

        if video is None:

            error(
                "Video tidak ditemukan."
            )

            return False

        srt_file = find_srt(
            video
        )

        if srt_file is None:

            error(
                "File SRT tidak ditemukan."
            )

            error(
                f"Folder: {TRANSCRIPT_DIR}"
            )

            return False

        info(
            f"SRT: {srt_file}"
        )

        command.append(
            str(srt_file)
        )

    # ========================================================
    # GENERATE CANDIDATES
    # ========================================================

    elif script == "generate_candidates_v2.py":

        transcript_file = (
            ANALYSIS_DIR
            /
            "transcript.json"
        )

        if not transcript_file.exists():

            error(
                "analysis/transcript.json "
                "tidak ditemukan."
            )

            return False

        info(
            f"Transcript: {transcript_file}"
        )

        command.append(
            str(transcript_file)
        )

    # ========================================================
    # REFINE
    # ========================================================

    elif script == "refine_clips.py":

        transcript_file = (
            ANALYSIS_DIR
            /
            "transcript.json"
        )

        if not transcript_file.exists():

            error(
                "analysis/transcript.json "
                "tidak ditemukan."
            )

            return False

    # ========================================================
    # FINALIZE
    # ========================================================

    elif script == "finalize_clips.py":

        refined_file = (
            ANALYSIS_DIR
            /
            "refined_clips.json"
        )

        if not refined_file.exists():

            error(
                "analysis/refined_clips.json "
                "tidak ditemukan."
            )

            return False

    # ========================================================
    # EXPORT CLIPS
    # ========================================================

    elif script == "export_clips.py":

        final_file = (
            ANALYSIS_DIR
            /
            "final_clips.json"
        )

        if not final_file.exists():

            error(
                "analysis/final_clips.json "
                "tidak ditemukan."
            )

            return False

        info(
            f"Final clips: {final_file}"
        )

    # ========================================================
    # VERTICAL
    # ========================================================

    elif script == "vertical_clips.py":

        clips = list(
            CLIPS_DIR.glob(
                "clip_*.mp4"
            )
        )

        if not clips:

            error(
                "Tidak ada clip di folder:"
            )

            error(
                f"{CLIPS_DIR}"
            )

            return False

        info(
            f"Input clips: {len(clips)}"
        )

    # ========================================================
    # SUBTITLE
    # ========================================================

    elif script == "subtitle_clips.py":

        final_file = (
            ANALYSIS_DIR
            /
            "final_clips.json"
        )

        if not final_file.exists():

            error(
                "analysis/final_clips.json "
                "tidak ditemukan."
            )

            return False

        vertical_files = list(
            VERTICAL_DIR.glob(
                "short_*.mp4"
            )
        )

        if not vertical_files:

            error(
                "Tidak ada vertical clips."
            )

            return False

        info(
            f"Vertical clips: "
            f"{len(vertical_files)}"
        )

    # ========================================================
    # SHOW COMMAND
    # ========================================================

    print()

    print(
        "▶",
        " ".join(
            f'"{x}"'
            if " " in str(x)
            else str(x)
            for x in command
        )
    )

    print()

    # ========================================================
    # EXECUTE
    # ========================================================

    start_time = datetime.now()

    result = subprocess.run(
        command,
        cwd=BASE_DIR
    )

    elapsed = (
        datetime.now()
        -
        start_time
    )

    print()

    # ========================================================
    # FAILED
    # ========================================================

    if result.returncode != 0:

        error(
            f"{script} gagal!"
        )

        error(
            f"Exit code: "
            f"{result.returncode}"
        )

        print()

        return False

    # ========================================================
    # SUCCESS
    # ========================================================

    success(
        f"{label} selesai "
        f"({elapsed.total_seconds():.1f}s)"
    )

    return True


# ============================================================
# VERIFY OUTPUT
# ============================================================

def verify_outputs():

    title(
        "🔍 VERIFY OUTPUT"
    )

    # --------------------------------------------------------
    # ANALYSIS FILES
    # --------------------------------------------------------

    checks = [

        (
            ANALYSIS_DIR /
            "transcript.json",

            "Transcript"
        ),

        (
            ANALYSIS_DIR /
            "refined_clips.json",

            "Refined clips"
        ),

        (
            ANALYSIS_DIR /
            "final_clips.json",

            "Final clips"
        ),
    ]

    for path, label in checks:

        if path.exists():

            success(
                f"{label}: OK"
            )

        else:

            error(
                f"{label}: "
                f"TIDAK DITEMUKAN"
            )

            return False

    # --------------------------------------------------------
    # EXPORTED CLIPS
    # --------------------------------------------------------

    clip_files = list(
        CLIPS_DIR.glob(
            "clip_*.mp4"
        )
    )

    # --------------------------------------------------------
    # VERTICAL
    # --------------------------------------------------------

    vertical_files = list(
        VERTICAL_DIR.glob(
            "short_*.mp4"
        )
    )

    # --------------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------------

    subtitle_files = list(
        SUBTITLED_DIR.glob(
            "final_*.mp4"
        )
    )

    print()

    info(
        f"Exported clips : "
        f"{len(clip_files)}"
    )

    info(
        f"Vertical clips : "
        f"{len(vertical_files)}"
    )

    info(
        f"Final videos   : "
        f"{len(subtitle_files)}"
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if not clip_files:

        error(
            "Tidak ada exported clips."
        )

        return False

    if not vertical_files:

        error(
            "Tidak ada vertical clips."
        )

        return False

    if not subtitle_files:

        error(
            "Tidak ada final videos."
        )

        return False

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    title(
        "🔥 CLIPPER MACHINE V1"
    )

    print(
        "ONE COMMAND → FULL PIPELINE"
    )

    print()

    # ========================================================
    # CHECK REQUIRED FILES
    # ========================================================

    if not check_required_files():

        print()

        error(
            "Pipeline dibatalkan."
        )

        return 1

    # ========================================================
    # FIND VIDEO
    # ========================================================

    video = find_input_video()

    if video is None:

        error(
            "Tidak ada video di folder:"
        )

        print(
            f"   {INPUT_DIR}"
        )

        print()

        print(
            "Masukkan video baru ke folder "
            "'input' lalu jalankan:"
        )

        print()

        print(
            "   py run.py"
        )

        return 1

    # ========================================================
    # INPUT INFO
    # ========================================================

    title(
        "🎬 INPUT VIDEO"
    )

    success(
        video.name
    )

    info(
        f"Location: {video}"
    )

    # ========================================================
    # CLEAN
    # ========================================================

    clean_old_outputs()

    # ========================================================
    # PIPELINE
    # ========================================================

    for label, script in SCRIPTS:

        ok = run_script(
            label,
            script,
            video
        )

        if not ok:

            title(
                "💥 PIPELINE STOPPED"
            )

            error(
                f"Gagal pada step: "
                f"{label}"
            )

            print()

            print(
                "Cek error di atas."
            )

            return 1

    # ========================================================
    # VERIFY
    # ========================================================

    ok = verify_outputs()

    if not ok:

        title(
            "⚠ PIPELINE SELESAI "
            "DENGAN MASALAH"
        )

        return 1

    # ========================================================
    # DONE
    # ========================================================

    title(
        "🎉 CLIPPER MACHINE SELESAI"
    )

    print()

    success(
        "Semua proses selesai!"
    )

    print()

    print(
        "🎬 Final videos:"
    )

    print(
        f"   {SUBTITLED_DIR}\\"
    )

    print()

    print(
        "📱 Vertical clips:"
    )

    print(
        f"   {VERTICAL_DIR}\\"
    )

    print()

    print(
        "✂️ Raw clips:"
    )

    print(
        f"   {CLIPS_DIR}\\"
    )

    print()

    print(
        "📊 Analysis:"
    )

    print(
        f"   {ANALYSIS_DIR}\\"
    )

    print()

    print(
        "🔥 Tinggal cek hasilnya bro!"
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