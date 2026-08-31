# ============================================================
# 🔥 CLIPPER MACHINE - ONE CLICK RUNNER V2
# FULL PIPELINE
#
# INPUT VIDEO
#     ↓
# TRANSCRIBE
#     ↓
# PARSE SRT
#     ↓
# CANDIDATE GENERATOR V4
#     ↓
# AI SCORER V4
#     ↓
# FINALIZER
#     ↓
# EXPORT CLIPS
#     ↓
# VERTICAL
#     ↓
# SUBTITLE
#     ↓
# FINAL VIDEO
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
    ("CANDIDATE GENERATOR V4", "candidate_generator.py"),
    ("AI SCORER V4", "ai_scorer.py"),
    ("FINALIZER", "finalize_clips.py"),
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
        if (
            p.is_file()
            and
            p.suffix.lower() in extensions
        )
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
    # PRIORITY 1
    # SRT dengan nama sama seperti video
    # --------------------------------------------------------

    expected = (
        TRANSCRIPT_DIR
        /
        f"{video.stem}.srt"
    )

    if expected.exists():

        return expected

    # --------------------------------------------------------
    # PRIORITY 2
    # SRT terbaru
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
# CHECK REQUIRED FILES
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

    folders = [
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

        "ai_scored_candidates.json",

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
# VERIFY FILE
# ============================================================

def require_file(path, label):

    if not path.exists():

        error(
            f"{label} tidak ditemukan:"
        )

        error(
            str(path)
        )

        return False

    success(
        f"{label}: OK"
    )

    return True


# ============================================================
# VERIFY MULTIPLE FILES
# ============================================================

def require_files(files, label):

    files = list(files)

    if not files:

        error(
            f"{label} tidak ditemukan."
        )

        return False

    success(
        f"{label}: {len(files)} file"
    )

    return True


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
    # CANDIDATE GENERATOR
    # ========================================================

    elif script == "candidate_generator.py":

        transcript_file = (
            ANALYSIS_DIR
            /
            "transcript.json"
        )

        if not require_file(
            transcript_file,
            "Transcript"
        ):

            return False

        command.append(
            str(transcript_file)
        )

    # ========================================================
    # AI SCORER
    # ========================================================

    elif script == "ai_scorer.py":

        candidates_file = (
            ANALYSIS_DIR
            /
            "candidates.json"
        )

        if not require_file(
            candidates_file,
            "Candidates"
        ):

            return False

        command.append(
            str(candidates_file)
        )

    # ========================================================
    # FINALIZER
    # ========================================================

    elif script == "finalize_clips.py":

        scored_file = (
            ANALYSIS_DIR
            /
            "ai_scored_candidates.json"
        )

        if not require_file(
            scored_file,
            "AI scored candidates"
        ):

            return False

    # ========================================================
    # EXPORT
    # ========================================================

    elif script == "export_clips.py":

        final_file = (
            ANALYSIS_DIR
            /
            "final_clips.json"
        )

        if not require_file(
            final_file,
            "Final clips"
        ):

            return False

        if video is not None:

            info(
                f"Input video: {video}"
            )

    # ========================================================
    # VERTICAL
    # ========================================================

    elif script == "vertical_clips.py":

        clips = CLIPS_DIR.glob(
            "clip_*.mp4"
        )

        if not require_files(
            clips,
            "Exported clips"
        ):

            return False

    # ========================================================
    # SUBTITLE
    # ========================================================

    elif script == "subtitle_clips.py":

        final_file = (
            ANALYSIS_DIR
            /
            "final_clips.json"
        )

        if not require_file(
            final_file,
            "Final clips"
        ):

            return False

        vertical_files = VERTICAL_DIR.glob(
            "short_*.mp4"
        )

        if not require_files(
            vertical_files,
            "Vertical clips"
        ):

            return False

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

    try:

        result = subprocess.run(
            command,
            cwd=BASE_DIR
        )

    except KeyboardInterrupt:

        print()

        warning(
            "Pipeline dihentikan user."
        )

        return False

    except Exception as e:

        error(
            f"Gagal menjalankan {script}"
        )

        error(
            str(e)
        )

        return False

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
# VERIFY PIPELINE OUTPUT
# ============================================================

def verify_outputs():

    title(
        "🔍 VERIFY FINAL OUTPUT"
    )

    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    checks = [

        (
            ANALYSIS_DIR
            /
            "transcript.json",
            "Transcript"
        ),

        (
            ANALYSIS_DIR
            /
            "candidates.json",
            "Candidates"
        ),

        (
            ANALYSIS_DIR
            /
            "ai_scored_candidates.json",
            "AI scored candidates"
        ),

        (
            ANALYSIS_DIR
            /
            "final_clips.json",
            "Final clips"
        ),

    ]

    for path, label in checks:

        if not require_file(
            path,
            label
        ):

            return False

    # --------------------------------------------------------
    # EXPORTED
    # --------------------------------------------------------

    clip_files = list(
        CLIPS_DIR.glob(
            "clip_*.mp4"
        )
    )

    if not require_files(
        clip_files,
        "Raw clips"
    ):

        return False

    # --------------------------------------------------------
    # VERTICAL
    # --------------------------------------------------------

    vertical_files = list(
        VERTICAL_DIR.glob(
            "short_*.mp4"
        )
    )

    if not require_files(
        vertical_files,
        "Vertical clips"
    ):

        return False

    # --------------------------------------------------------
    # SUBTITLED
    # --------------------------------------------------------

    subtitle_files = list(
        SUBTITLED_DIR.glob(
            "final_*.mp4"
        )
    )

    if not require_files(
        subtitle_files,
        "Final subtitled videos"
    ):

        return False

    # --------------------------------------------------------
    # COUNT CHECK
    # --------------------------------------------------------

    print()

    info(
        f"Raw clips       : "
        f"{len(clip_files)}"
    )

    info(
        f"Vertical clips  : "
        f"{len(vertical_files)}"
    )

    info(
        f"Final videos    : "
        f"{len(subtitle_files)}"
    )

    # --------------------------------------------------------
    # COUNT MISMATCH
    # --------------------------------------------------------

    if len(clip_files) != len(vertical_files):

        warning(
            "Jumlah raw clips dan vertical "
            "clips berbeda."
        )

    if len(vertical_files) != len(subtitle_files):

        warning(
            "Jumlah vertical clips dan final "
            "videos berbeda."
        )

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    title(
        "🔥 CLIPPER MACHINE V2"
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

    success(
        "Semua script pipeline ditemukan."
    )

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
            "Masukkan video ke folder "
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
        "🎬 FINAL VIDEOS"
    )

    print(
        f"   {SUBTITLED_DIR}\\"
    )

    print()

    print(
        "📱 VERTICAL"
    )

    print(
        f"   {VERTICAL_DIR}\\"
    )

    print()

    print(
        "✂️ RAW CLIPS"
    )

    print(
        f"   {CLIPS_DIR}\\"
    )

    print()

    print(
        "📊 ANALYSIS"
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