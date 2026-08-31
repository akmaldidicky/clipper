# ============================================================
# 🔥 YOUTUBE CLIPPER MACHINE V2
#
# YOUTUBE URL
#      ↓
# CHECK INDONESIAN SUBTITLE
#      ↓
# DOWNLOAD SRT
#      ↓
# DOWNLOAD VIDEO
#      ↓
# PARSE SRT
#      ↓
# CANDIDATE GENERATOR V4
#      ↓
# AI SCORER V4
#      ↓
# FINALIZER V2
#      ↓
# EXPORT CLIPS
#      ↓
# VERTICAL
#      ↓
# SUBTITLE
#      ↓
# FINAL VIDEO
#
# NO WHISPER
# ============================================================

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shutil


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# DIRECTORIES
# ============================================================

INPUT_DIR = BASE_DIR / "input"
TRANSCRIPT_DIR = BASE_DIR / "transcripts"
ANALYSIS_DIR = BASE_DIR / "analysis"
CLIPS_DIR = BASE_DIR / "clips"
VERTICAL_DIR = BASE_DIR / "vertical"
SUBTITLED_DIR = BASE_DIR / "subtitled"


# ============================================================
# YOUTUBE OUTPUT
# ============================================================

VIDEO_FILE = INPUT_DIR / "pidio.mp4"
SRT_FILE = TRANSCRIPT_DIR / "youtube.srt"


# ============================================================
# ANALYSIS FILES
# ============================================================

TRANSCRIPT_JSON = (
    ANALYSIS_DIR /
    "transcript.json"
)

CANDIDATES_JSON = (
    ANALYSIS_DIR /
    "candidates.json"
)

AI_JSON = (
    ANALYSIS_DIR /
    "ai_scored_candidates.json"
)

FINAL_JSON = (
    ANALYSIS_DIR /
    "final_clips.json"
)


# ============================================================
# PIPELINE SCRIPTS
# ============================================================

REQUIRED_SCRIPTS = [

    "parse_srt.py",

    "candidate_generator.py",

    "ai_scorer.py",

    "finalize_clips_v2.py",

    "export_clips.py",

    "vertical_clips.py",

    "subtitle_clips.py",

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
# CHECK COMMAND
# ============================================================

def check_command(command):

    return shutil.which(command) is not None


# ============================================================
# CHECK YT-DLP
# ============================================================

def check_ytdlp():

    title(
        "🔍 CHECKING YT-DLP"
    )

    # --------------------------------------------------------
    # IMPORTANT
    #
    # Windows user sebelumnya:
    #
    # py -m yt_dlp --version
    #
    # Jadi kita prioritaskan module.
    # --------------------------------------------------------

    try:

        result = subprocess.run(

            [
                sys.executable,
                "-m",
                "yt_dlp",
                "--version"
            ],

            capture_output=True,

            text=True

        )

        if result.returncode == 0:

            version = (
                result.stdout
                .strip()
            )

            success(
                f"yt-dlp OK "
                f"(version {version})"
            )

            return True

    except Exception:

        pass

    # --------------------------------------------------------
    # Fallback executable
    # --------------------------------------------------------

    if check_command("yt-dlp"):

        success(
            "yt-dlp OK"
        )

        return True

    # --------------------------------------------------------
    # Failed
    # --------------------------------------------------------

    error(
        "yt-dlp tidak ditemukan."
    )

    print()

    print(
        "Install dengan:"
    )

    print(
        "py -m pip install -U yt-dlp"
    )

    return False


# ============================================================
# YT-DLP COMMAND
# ============================================================

def ytdlp_command():

    # Prefer:
    #
    # py -m yt_dlp
    #
    # Karena ini sudah terbukti bekerja
    # di environment user.

    return [

        sys.executable,

        "-m",

        "yt_dlp"

    ]


# ============================================================
# CHECK FFMPEG
# ============================================================

def check_ffmpeg():

    title(
        "🔍 CHECKING FFMPEG"
    )

    if not check_command(
        "ffmpeg"
    ):

        error(
            "FFmpeg tidak ditemukan."
        )

        return False

    try:

        result = subprocess.run(

            [
                "ffmpeg",
                "-version"
            ],

            capture_output=True,

            text=True

        )

        if result.returncode == 0:

            first_line = (
                result.stdout
                .splitlines()[0]
                if result.stdout
                else
                "FFmpeg"
            )

            success(
                first_line
            )

            return True

    except Exception as e:

        error(
            str(e)
        )

    return False


# ============================================================
# CHECK PIPELINE SCRIPTS
# ============================================================

def check_pipeline_scripts():

    title(
        "🔍 CHECKING PIPELINE"
    )

    missing = []

    for script in REQUIRED_SCRIPTS:

        path = (
            BASE_DIR /
            script
        )

        if not path.exists():

            missing.append(
                script
            )

        else:

            success(
                script
            )

    if missing:

        print()

        error(
            "Script pipeline tidak lengkap."
        )

        for script in missing:

            print(
                f"   - {script}"
            )

        return False

    print()

    success(
        "Semua script pipeline tersedia."
    )

    return True


# ============================================================
# CHECK YOUTUBE SUBTITLE
# ============================================================

def check_subtitles(url):

    title(
        "🔍 CHECKING YOUTUBE SUBTITLES"
    )

    command = (

        ytdlp_command()

        +

        [

            "--list-subs",

            "--skip-download",

            url

        ]

    )

    try:

        result = subprocess.run(

            command,

            capture_output=True,

            text=True

        )

    except Exception as e:

        error(
            f"Gagal menjalankan yt-dlp: {e}"
        )

        return False


    if result.returncode != 0:

        error(
            "Gagal membaca subtitle YouTube."
        )

        if result.stderr:

            print(
                result.stderr
            )

        return False


    output = (

        result.stdout

        +

        result.stderr

    )


    output_lower = (
        output.lower()
    )


    # --------------------------------------------------------
    # IMPORTANT
    #
    # Kita hanya menerima Indonesian.
    #
    # Tidak fallback ke Whisper.
    # Tidak translate.
    # --------------------------------------------------------

    indicators = [

        "id",

        "id-id",

        "indonesian",

        "indonesia"

    ]


    found = False

    for indicator in indicators:

        if indicator in output_lower:

            found = True

            break


    if not found:

        print()

        error(
            "SUBTITLE INDONESIA TIDAK DITEMUKAN."
        )

        print()

        print(
            "Video tidak dapat diproses."
        )

        print(
            "Pipeline YouTube hanya menerima "
            "subtitle Indonesia."
        )

        return False


    print()

    success(
        "Subtitle Indonesia terdeteksi."
    )

    return True


# ============================================================
# CLEAN OLD YOUTUBE FILES
# ============================================================

def clean_youtube_files():

    title(
        "🧹 CLEAN YOUTUBE OUTPUT"
    )

    # --------------------------------------------------------
    # SRT
    # --------------------------------------------------------

    if SRT_FILE.exists():

        SRT_FILE.unlink()

        info(
            f"Hapus {SRT_FILE}"
        )


    # --------------------------------------------------------
    # VIDEO
    # --------------------------------------------------------

    if VIDEO_FILE.exists():

        VIDEO_FILE.unlink()

        info(
            f"Hapus {VIDEO_FILE}"
        )


# ============================================================
# CLEAN PIPELINE OUTPUT
# ============================================================

def clean_pipeline_outputs():

    title(
        "🧹 CLEAN OLD PIPELINE OUTPUT"
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

            ANALYSIS_DIR /
            filename

        )

        if path.exists():

            path.unlink()

            info(
                f"Hapus {path}"
            )


    # --------------------------------------------------------
    # RAW CLIPS
    # --------------------------------------------------------

    for file in CLIPS_DIR.glob(
        "clip_*.mp4"
    ):

        file.unlink()

        info(
            f"Hapus {file}"
        )


    # --------------------------------------------------------
    # VERTICAL
    # --------------------------------------------------------

    for file in VERTICAL_DIR.glob(
        "short_*.mp4"
    ):

        file.unlink()

        info(
            f"Hapus {file}"
        )


    # --------------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------------

    for file in SUBTITLED_DIR.glob(
        "final_*.mp4"
    ):

        file.unlink()

        info(
            f"Hapus {file}"
        )


# ============================================================
# DOWNLOAD SUBTITLE
# ============================================================

def download_subtitle(url):

    title(
        "📥 DOWNLOAD SUBTITLE INDONESIA"
    )

    TRANSCRIPT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # Remove old youtube SRT
    # --------------------------------------------------------

    if SRT_FILE.exists():

        SRT_FILE.unlink()


    # --------------------------------------------------------
    # Remove possible old generated files
    # --------------------------------------------------------

    for file in TRANSCRIPT_DIR.glob(
        "youtube*.srt"
    ):

        try:

            file.unlink()

        except Exception:

            pass


    # --------------------------------------------------------
    # yt-dlp
    # --------------------------------------------------------

    command = (

        ytdlp_command()

        +

        [

            "--skip-download",

            "--write-subs",

            "--write-auto-subs",

            "--sub-langs",

            "id,id-ID",

            "--sub-format",

            "srt",

            "--output",

            str(

                TRANSCRIPT_DIR /
                "youtube.%(ext)s"

            ),

            url

        ]

    )


    print()

    print(
        "▶",
        " ".join(
            str(x)
            for x in command
        )
    )

    print()


    try:

        result = subprocess.run(
            command
        )

    except Exception as e:

        error(
            str(e)
        )

        return False


    if result.returncode != 0:

        error(
            "Gagal download subtitle."
        )

        return False


    # --------------------------------------------------------
    # Find exact files first
    # --------------------------------------------------------

    possible_files = [

        TRANSCRIPT_DIR /
        "youtube.id.srt",

        TRANSCRIPT_DIR /
        "youtube.id-ID.srt",

        TRANSCRIPT_DIR /
        "youtube.srt",

    ]


    found = None


    for file in possible_files:

        if file.exists():

            found = file

            break


    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if found is None:

        files = sorted(

            TRANSCRIPT_DIR.glob(
                "youtube*.srt"
            )

        )


        if files:

            found = files[0]


    # --------------------------------------------------------
    # No SRT
    # --------------------------------------------------------

    if found is None:

        error(
            "Subtitle diminta tetapi file SRT "
            "tidak ditemukan."
        )

        return False


    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if found.stat().st_size == 0:

        error(
            "SRT kosong."
        )

        return False


    # --------------------------------------------------------
    # Rename
    # --------------------------------------------------------

    if found != SRT_FILE:

        if SRT_FILE.exists():

            SRT_FILE.unlink()

        found.rename(
            SRT_FILE
        )


    print()

    success(
        "SRT downloaded:"
    )

    print(
        f"   {SRT_FILE}"
    )

    return True


# ============================================================
# DOWNLOAD VIDEO
# ============================================================

def download_video(url):

    title(
        "📥 DOWNLOAD VIDEO"
    )

    INPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    if VIDEO_FILE.exists():

        VIDEO_FILE.unlink()


    # --------------------------------------------------------
    # IMPORTANT
    #
    # Output dipaksa menjadi:
    #
    # input/pidio.mp4
    # --------------------------------------------------------

    command = (

        ytdlp_command()

        +

        [

            "-f",

            "bv*+ba/b",

            "--merge-output-format",

            "mp4",

            "--output",

            str(
                VIDEO_FILE
            ),

            url

        ]

    )


    print()

    print(
        "▶",
        " ".join(
            str(x)
            for x in command
        )
    )

    print()


    try:

        result = subprocess.run(
            command
        )

    except Exception as e:

        error(
            str(e)
        )

        return False


    if result.returncode != 0:

        error(
            "Gagal download video."
        )

        return False


    if not VIDEO_FILE.exists():

        error(
            "Video tidak ditemukan setelah download."
        )

        return False


    size_mb = (

        VIDEO_FILE.stat().st_size

        /

        (1024 * 1024)

    )


    print()

    success(
        "Video downloaded:"
    )

    print(
        f"   {VIDEO_FILE}"
    )

    info(
        f"Size: {size_mb:.2f} MB"
    )

    return True


# ============================================================
# RUN SCRIPT
# ============================================================

def run_script(
    label,
    script,
    args=None
):

    title(
        f"🔥 {label}"
    )


    if args is None:

        args = []


    script_path = (

        BASE_DIR /
        script

    )


    command = [

        sys.executable,

        str(script_path)

    ]


    command.extend(
        args
    )


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
            str(e)
        )

        return False


    elapsed = (

        datetime.now()
        -
        start_time

    )


    if result.returncode != 0:

        print()

        error(
            f"{script} gagal!"
        )

        error(
            f"Exit code: "
            f"{result.returncode}"
        )

        return False


    print()

    success(

        f"{label} selesai "

        f"({elapsed.total_seconds():.1f}s)"

    )


    return True


# ============================================================
# VERIFY FILE
# ============================================================

def require_file(
    path,
    label
):

    if not path.exists():

        error(
            f"{label} tidak ditemukan:"
        )

        print(
            f"   {path}"
        )

        return False


    success(
        f"{label}: OK"
    )

    return True


# ============================================================
# VERIFY MULTIPLE FILES
# ============================================================

def require_files(
    files,
    label
):

    files = list(files)


    if not files:

        error(
            f"{label} tidak ditemukan."
        )

        return False


    success(
        f"{label}: "
        f"{len(files)} file"
    )

    return True


# ============================================================
# RUN EXISTING PIPELINE
# ============================================================

def run_pipeline():

    # ========================================================
    # 1. PARSE SRT
    # ========================================================

    if not run_script(

        "SRT PARSER",

        "parse_srt.py",

        [

            str(SRT_FILE)

        ]

    ):

        return False


    # ========================================================
    # 2. CANDIDATE GENERATOR
    # ========================================================

    if not require_file(

        TRANSCRIPT_JSON,

        "Transcript"

    ):

        return False


    if not run_script(

        "CANDIDATE GENERATOR V4",

        "candidate_generator.py",

        [

            str(TRANSCRIPT_JSON)

        ]

    ):

        return False


    # ========================================================
    # 3. AI SCORER
    # ========================================================

    if not require_file(

        CANDIDATES_JSON,

        "Candidates"

    ):

        return False


    if not run_script(

        "AI SCORER V4",

        "ai_scorer.py",

        [

            str(CANDIDATES_JSON)

        ]

    ):

        return False


    # ========================================================
    # 4. FINALIZER V2
    # ========================================================

    if not require_file(

        AI_JSON,

        "AI scored candidates"

    ):

        return False


    if not run_script(

        "FINALIZER V2",

        "finalize_clips_v2.py"

    ):

        return False


    # ========================================================
    # 5. EXPORT
    # ========================================================

    if not require_file(

        FINAL_JSON,

        "Final clips"

    ):

        return False


    if not run_script(

        "EXPORT CLIPS",

        "export_clips.py"

    ):

        return False


    # ========================================================
    # 6. VERIFY RAW CLIPS
    # ========================================================

    raw_clips = list(

        CLIPS_DIR.glob(
            "clip_*.mp4"
        )

    )


    if not require_files(

        raw_clips,

        "Raw clips"

    ):

        return False


    # ========================================================
    # 7. VERTICAL
    # ========================================================

    if not run_script(

        "VERTICAL",

        "vertical_clips.py"

    ):

        return False


    # ========================================================
    # 8. VERIFY VERTICAL
    # ========================================================

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


    # ========================================================
    # 9. SUBTITLE
    # ========================================================

    if not run_script(

        "SUBTITLE",

        "subtitle_clips.py"

    ):

        return False


    # ========================================================
    # 10. VERIFY FINAL
    # ========================================================

    final_files = list(

        SUBTITLED_DIR.glob(
            "final_*.mp4"
        )

    )


    if not require_files(

        final_files,

        "Final subtitled videos"

    ):

        return False


    return True


# ============================================================
# FINAL REPORT
# ============================================================

def final_report():

    title(
        "🎉 YOUTUBE CLIPPER SELESAI"
    )


    raw_clips = list(

        CLIPS_DIR.glob(
            "clip_*.mp4"
        )

    )


    vertical_files = list(

        VERTICAL_DIR.glob(
            "short_*.mp4"
        )

    )


    final_files = list(

        SUBTITLED_DIR.glob(
            "final_*.mp4"
        )

    )


    print()

    success(
        f"Raw clips      : "
        f"{len(raw_clips)}"
    )

    success(
        f"Vertical clips : "
        f"{len(vertical_files)}"
    )

    success(
        f"Final videos   : "
        f"{len(final_files)}"
    )


    print()

    print(
        "🎬 FINAL VIDEOS"
    )

    print(
        f"   {SUBTITLED_DIR}\\"
    )


    print()

    for file in sorted(
        final_files
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

    success(
        "SEMUA PROSES SELESAI!"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    title(
        "🔥 CLIPPER MACHINE — YOUTUBE V2"
    )

    print(
        "YouTube URL"
        " → SRT"
        " → VIDEO"
        " → AI"
        " → CLIPS"
        " → VERTICAL"
        " → SUBTITLE"
        " → FINAL"
    )


    # ========================================================
    # URL
    # ========================================================

    if len(sys.argv) < 2:

        print()

        error(
            "URL YouTube belum diberikan."
        )

        print()

        print(
            "Usage:"
        )

        print()

        print(

            'py youtube_run.py '
            '"https://www.youtube.com/watch?v=XXXXX"'

        )

        return 1


    url = sys.argv[1].strip()


    if not url:

        error(
            "URL kosong."
        )

        return 1


    print()

    print(
        "YouTube URL:"
    )

    print(
        url
    )


    # ========================================================
    # DEPENDENCIES
    # ========================================================

    if not check_ytdlp():

        return 1


    if not check_ffmpeg():

        return 1


    if not check_pipeline_scripts():

        return 1


    # ========================================================
    # CHECK SUBTITLE
    # ========================================================

    if not check_subtitles(url):

        return 1


    # ========================================================
    # CLEAN YOUTUBE FILES
    # ========================================================

    clean_youtube_files()


    # ========================================================
    # CLEAN PIPELINE
    # ========================================================

    clean_pipeline_outputs()


    # ========================================================
    # DOWNLOAD SRT
    # ========================================================

    if not download_subtitle(url):

        title(
            "💥 PIPELINE STOPPED"
        )

        error(
            "Subtitle YouTube tidak berhasil "
            "didownload."
        )

        return 1


    # ========================================================
    # DOWNLOAD VIDEO
    # ========================================================

    if not download_video(url):

        title(
            "💥 PIPELINE STOPPED"
        )

        error(
            "Video YouTube tidak berhasil "
            "didownload."
        )

        return 1


    # ========================================================
    # RUN PIPELINE
    # ========================================================

    success(
        "Input YouTube siap."
    )

    print()

    info(
        f"Video : {VIDEO_FILE}"
    )

    info(
        f"SRT   : {SRT_FILE}"
    )


    if not run_pipeline():

        title(
            "💥 YOUTUBE PIPELINE STOPPED"
        )

        error(
            "Pipeline gagal."
        )

        print()

        print(
            "Cek error pada step terakhir."
        )

        return 1


    # ========================================================
    # FINAL
    # ========================================================

    final_report()


    return 0


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )