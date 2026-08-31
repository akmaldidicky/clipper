# ============================================================
# 🔥 CLIPPER MACHINE — THUMBNAIL GENERATOR V4
#
# Frame pertama dari vertical video
# + Judul AI dari final_clips.json
#
# STYLE:
# - Center horizontal
# - Center vertikal
# - Arial Bold
# - White text
# - Black outline
# - Shadow
# - Semi-transparent black box
# - Automatic word wrap
# - Maximum 3 lines
#
# FIX:
# - Tidak menggunakan font='Arial'
# - Menggunakan fontfile Windows
# - Tidak menggunakan \n langsung di drawtext
# - Menggunakan textfile untuk multiline
# - Aman dari masalah ":n"
# ============================================================

import json
import subprocess
import shutil
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

VERTICAL_DIR = BASE_DIR / "vertical"

CLIPS_FILE = (
    BASE_DIR
    / "analysis"
    / "final_clips.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "thumbnails"
)

TEMP_DIR = (
    BASE_DIR
    / "temp_thumbnail_text"
)


# ============================================================
# VIDEO
# ============================================================

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920


# ============================================================
# TITLE
# ============================================================

FONT_SIZE = 82

MAX_TITLE_LINES = 3

MAX_CHARS_PER_LINE = 24

# CENTER VERTIKAL
TITLE_Y = "(h-text_h)/2"

LINE_SPACING = 8


# ============================================================
# STYLE
# ============================================================

FONT_COLOR = "0xFFD21F"
BORDER_WIDTH = 9
BORDER_COLOR = "black"
SHADOW_X = 5
SHADOW_Y = 5

BOX = 1
BOX_COLOR = "black@0.65"
BOX_BORDER_W = 28


# ============================================================
# BACKGROUND BOX
# ============================================================

BOX = 1

BOX_COLOR = "black@0.65"

BOX_BORDER_W = 25


# ============================================================
# FONT WINDOWS
# ============================================================

FONT_CANDIDATES = [

    Path(
        "C:/Windows/Fonts/arialbd.ttf"
    ),

    Path(
        "C:/Windows/Fonts/arial.ttf"
    ),

    Path(
        "C:/Windows/Fonts/Arial.ttf"
    ),

]


# ============================================================
# TERMINAL COLORS
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


def success(text):

    print(
        f"{GREEN}✅ {text}{RESET}"
    )


def error(text):

    print(
        f"{RED}❌ {text}{RESET}"
    )


def warning(text):

    print(
        f"{YELLOW}⚠ {text}{RESET}"
    )


def info(text):

    print(
        f"{CYAN}ℹ {text}{RESET}"
    )


# ============================================================
# CHECK FFMPEG
# ============================================================

def check_ffmpeg():

    print(
        "🔍 Checking FFmpeg..."
    )

    path = shutil.which(
        "ffmpeg"
    )

    if path is None:

        error(
            "FFmpeg tidak ditemukan."
        )

        return False

    success(
        "FFmpeg OK"
    )

    return True


# ============================================================
# FIND FONT
# ============================================================

def find_font():

    for font in FONT_CANDIDATES:

        if font.exists():

            return font

    return None


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
# CLEAN TITLE
# ============================================================

def clean_title(text):

    text = str(text)

    # --------------------------------------------------------
    # Hilangkan newline
    # --------------------------------------------------------

    text = text.replace(
        "\n",
        " "
    )

    text = text.replace(
        "\r",
        " "
    )

    # --------------------------------------------------------
    # Hilangkan whitespace berlebih
    # --------------------------------------------------------

    text = " ".join(
        text.split()
    )

    return text.strip()


# ============================================================
# WRAP TITLE
# ============================================================

def wrap_title(
    text,
    max_chars=MAX_CHARS_PER_LINE,
    max_lines=MAX_TITLE_LINES
):

    text = clean_title(
        text
    )

    if not text:

        return ""

    words = text.split()

    lines = []

    current = ""

    # ========================================================
    # WORD WRAPPING
    # ========================================================

    for word in words:

        # ----------------------------------------------------
        # Kalau kata terlalu panjang
        # ----------------------------------------------------

        if len(word) > max_chars:

            if current:

                lines.append(
                    current
                )

                current = ""

            while len(word) > max_chars:

                lines.append(
                    word[:max_chars]
                )

                word = word[
                    max_chars:
                ]

            if word:

                current = word

            continue

        # ----------------------------------------------------
        # Baris kosong
        # ----------------------------------------------------

        if not current:

            current = word

            continue

        # ----------------------------------------------------
        # Coba tambah kata
        # ----------------------------------------------------

        test = (
            current
            + " "
            + word
        )

        if len(test) <= max_chars:

            current = test

        else:

            lines.append(
                current
            )

            current = word

    # ========================================================
    # LAST LINE
    # ========================================================

    if current:

        lines.append(
            current
        )

    # ========================================================
    # MAX 3 LINES
    # ========================================================

    if len(lines) <= max_lines:

        return "\n".join(
            lines
        )

    # ========================================================
    # GABUNG SISA KE BARIS TERAKHIR
    # ========================================================

    first_lines = lines[
        :max_lines - 1
    ]

    remaining = " ".join(
        lines[
            max_lines - 1:
        ]
    )

    # ========================================================
    # TRUNCATE
    # ========================================================

    if len(remaining) > max_chars:

        remaining = (
            remaining[
                :max_chars - 3
            ]
            + "..."
        )

    first_lines.append(
        remaining
    )

    return "\n".join(
        first_lines
    )


# ============================================================
# ESCAPE FFMPEG FILTER PATH
# ============================================================

def escape_filter_path(path):

    path = str(
        Path(path).resolve()
    )

    # Windows \ → /
    path = path.replace(
        "\\",
        "/"
    )

    # Escape :
    path = path.replace(
        ":",
        "\\:"
    )

    # Escape single quote
    path = path.replace(
        "'",
        "\\'"
    )

    return path


# ============================================================
# CREATE TEXT FILE
# ============================================================

def create_text_file(
    text,
    output_file
):

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            text
        )

    return output_file


# ============================================================
# CREATE THUMBNAIL
# ============================================================

def create_thumbnail(
    input_file,
    output_file,
    title_text,
    font_file,
    text_file
):

    # ========================================================
    # WRAP
    # ========================================================

    wrapped = wrap_title(
        title_text
    )

    print()

    print(
        "📝 Judul:"
    )

    print(
        wrapped
    )

    # ========================================================
    # SAVE TEXT
    # ========================================================

    create_text_file(
        wrapped,
        text_file
    )

    # ========================================================
    # ESCAPE PATH
    # ========================================================

    font_path = escape_filter_path(
        font_file
    )

    text_path = escape_filter_path(
        text_file
    )

    # ========================================================
    # DRAW TEXT
    # ========================================================

    drawtext = (

        "drawtext="

        f"fontfile='{font_path}':"

        f"textfile='{text_path}':"

        f"fontsize={FONT_SIZE}:"

        f"fontcolor={FONT_COLOR}:"

        f"borderw={BORDER_WIDTH}:"

        f"bordercolor={BORDER_COLOR}:"

        f"shadowx={SHADOW_X}:"

        f"shadowy={SHADOW_Y}:"

        f"box={BOX}:"

        f"boxcolor={BOX_COLOR}:"

        f"boxborderw={BOX_BORDER_W}:"

        "x=(w-text_w)/2:"

        f"y={TITLE_Y}:"

        f"line_spacing={LINE_SPACING}"

    )

    # ========================================================
    # FFMPEG COMMAND
    # ========================================================

    command = [

        "ffmpeg",

        "-y",

        "-i",
        str(input_file),

        "-vf",
        drawtext,

        "-frames:v",
        "1",

        "-q:v",
        "2",

        str(output_file)

    ]

    print()

    print(
        "▶ Membuat thumbnail..."
    )

    print()

    result = subprocess.run(
        command
    )

    return (
        result.returncode == 0
        and
        output_file.exists()
    )


# ============================================================
# GET TITLE
# ============================================================

def get_title_from_clip(
    clip
):

    # ========================================================
    # PRIORITAS
    # ========================================================

    possible_fields = [

        "title",

        "hook",

        "name",

    ]

    for field in possible_fields:

        value = clip.get(
            field
        )

        if value:

            return clean_title(
                value
            )

    return "CLIPPER MACHINE"


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # HEADER
    # ========================================================

    title(
        "🔥 CLIPPER MACHINE — THUMBNAIL GENERATOR V4"
    )

    print()

    print(
        "Frame   : pertama"
    )

    print(
        "Position: CENTER"
    )

    print(
        "Style   : Bold + outline + shadow + dark box"
    )

    print()

    # ========================================================
    # CHECK FFMPEG
    # ========================================================

    if not check_ffmpeg():

        return 1

    # ========================================================
    # FONT
    # ========================================================

    font_file = find_font()

    if font_file is None:

        error(
            "Font Arial Windows tidak ditemukan."
        )

        print()

        print(
            "Dicari di:"
        )

        for font in FONT_CANDIDATES:

            print(
                f"   {font}"
            )

        return 1

    success(
        f"Font: {font_file}"
    )

    # ========================================================
    # LOAD CLIPS
    # ========================================================

    try:

        clips = load_json(
            CLIPS_FILE
        )

    except Exception as e:

        error(
            str(e)
        )

        return 1

    # ========================================================
    # DIRECTORIES
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    TEMP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # CLEAN OLD THUMBNAILS
    # ========================================================

    for file in OUTPUT_DIR.glob(
        "thumbnail_*.jpg"
    ):

        try:

            file.unlink()

        except Exception:

            pass

    # ========================================================
    # CLEAN OLD TEXT
    # ========================================================

    for file in TEMP_DIR.glob(
        "title_*.txt"
    ):

        try:

            file.unlink()

        except Exception:

            pass

    # ========================================================
    # INFO
    # ========================================================

    print()

    print(
        f"Vertical videos : {len(clips)}"
    )

    print(
        f"Output          : {OUTPUT_DIR.name}"
    )

    print(
        "Frame           : pertama"
    )

    print(
        "Position        : center"
    )

    print(
        "Title           : AI final clips"
    )

    # ========================================================
    # COUNTER
    # ========================================================

    success_count = 0

    failed_count = 0

    # ========================================================
    # PROCESS
    # ========================================================

    for index, clip in enumerate(
        clips,
        1
    ):

        # ----------------------------------------------------
        # INPUT
        # ----------------------------------------------------

        input_file = (

            VERTICAL_DIR
            /
            f"short_{index:03d}.mp4"

        )

        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        output_file = (

            OUTPUT_DIR
            /
            f"thumbnail_{index:03d}.jpg"

        )

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        text_file = (

            TEMP_DIR
            /
            f"title_{index:03d}.txt"

        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title_text = get_title_from_clip(
            clip
        )

        # ====================================================
        # HEADER
        # ====================================================

        print()

        print(
            "-" * 70
        )

        print(
            f"🎬 THUMBNAIL {index}"
        )

        print(
            f"Input : {input_file}"
        )

        print(
            f"Title : {title_text}"
        )

        print(
            "-" * 70
        )

        # ====================================================
        # CHECK VIDEO
        # ====================================================

        if not input_file.exists():

            error(
                f"Video tidak ditemukan: "
                f"{input_file}"
            )

            failed_count += 1

            continue

        # ====================================================
        # CREATE
        # ====================================================

        try:

            ok = create_thumbnail(

                input_file,

                output_file,

                title_text,

                font_file,

                text_file

            )

        except Exception as e:

            error(
                f"Exception: {e}"
            )

            ok = False

        # ====================================================
        # RESULT
        # ====================================================

        if ok:

            success_count += 1

            print()

            success(
                f"DONE → {output_file}"
            )

        else:

            failed_count += 1

            error(
                "FAILED"
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 70)

    print(
        "🔥 THUMBNAIL GENERATOR SELESAI"
    )

    print("=" * 70)

    print()

    print(
        f"Total   : {len(clips)}"
    )

    print(
        f"Success : {success_count}"
    )

    print(
        f"Failed  : {failed_count}"
    )

    print()

    print(
        f"Output → {OUTPUT_DIR}\\"
    )

    print()

    # ========================================================
    # FINAL STATUS
    # ========================================================

    if failed_count:

        warning(
            "Ada thumbnail yang gagal."
        )

        return 1

    success(
        "Semua thumbnail berhasil dibuat! 🔥"
    )

    return 0


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )