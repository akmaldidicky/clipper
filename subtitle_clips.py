# ============================================================
# 🔥 SUBTITLE CLIPS V8.9
# FLAT CLEAN + AUTO OVERLAP TRIM
#
# FITUR:
# - Subtitle putih flat
# - Black outline
# - Shadow
# - Tanpa keyword highlight
# - Max 6 kata per caption
# - Max 3 kata per baris
# - ASS 72
# - Margin 360
# - Bottom center
# - AUTO TRIM OVERLAP
# - Caption lama langsung hilang saat caption baru muncul
# ============================================================

import json
import re
import subprocess
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

TRANSCRIPT_FILE = Path(
    "analysis/transcript.json"
)

CLIPS_FILE = Path(
    "analysis/final_clips.json"
)

INPUT_DIR = Path(
    "vertical"
)

OUTPUT_DIR = Path(
    "subtitled"
)

TEMP_SRT_DIR = Path(
    "temp_srt"
)

TEMP_ASS_DIR = Path(
    "temp_ass"
)


# ============================================================
# SUBTITLE
# ============================================================

MAX_WORDS_PER_CAPTION = 6

MAX_WORDS_PER_LINE = 3

MIN_CAPTION_DURATION = 0.75


# ============================================================
# OVERLAP
# ============================================================

# Durasi minimum caption setelah dipotong.
#
# Kalau hasil trimming kurang dari angka ini,
# caption tersebut dibuang agar tidak menghasilkan
# subtitle yang cuma muncul sangat sebentar.
#
MIN_OVERLAP_DURATION = 0.15


# ============================================================
# VISUAL
# ============================================================

FONT_NAME = "Arial"

# SRT baseline
FONT_SIZE = 18

# 🔒 LOCKED ASS SIZE
ASS_FONT_SIZE = 72

OUTLINE = 4

SHADOW = 2


# ============================================================
# POSITION
# ============================================================

# 🔒 LOCKED
ALIGNMENT = 2

# 🔒 LOCKED
MARGIN_VERTICAL = 360


# ============================================================
# COLORS
# ============================================================

WHITE = "&H00FFFFFF&"

BLACK = "&H00000000&"


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
# NORMALIZE TRANSCRIPT
# ============================================================

def normalize_transcript(data):

    if isinstance(data, list):

        segments = data

    elif isinstance(data, dict):

        if "segments" in data:

            segments = data["segments"]

        else:

            raise ValueError(
                "Transcript tidak punya 'segments'."
            )

    else:

        raise ValueError(
            "Format transcript tidak valid."
        )

    result = []

    for index, seg in enumerate(
        segments
    ):

        if (
            "start" not in seg
            or
            "end" not in seg
            or
            "text" not in seg
        ):

            continue

        text = str(
            seg["text"]
        ).strip()

        if not text:

            continue

        result.append({

            "id": index,

            "start": float(
                seg["start"]
            ),

            "end": float(
                seg["end"]
            ),

            "text": text

        })

    return result


# ============================================================
# TIME
# ============================================================

def srt_time(seconds):

    seconds = max(
        0,
        float(seconds)
    )

    hours = int(
        seconds // 3600
    )

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = int(
        seconds % 60
    )

    milliseconds = int(
        round(
            (
                seconds
                -
                int(seconds)
            )
            * 1000
        )
    )

    if milliseconds >= 1000:

        milliseconds -= 1000

        secs += 1

    if secs >= 60:

        secs -= 60

        minutes += 1

    if minutes >= 60:

        minutes -= 60

        hours += 1

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{milliseconds:03d}"
    )


def ass_time(seconds):

    seconds = max(
        0,
        float(seconds)
    )

    hours = int(
        seconds // 3600
    )

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = (
        seconds
        -
        hours * 3600
        -
        minutes * 60
    )

    return (
        f"{hours}:"
        f"{minutes:02d}:"
        f"{secs:05.2f}"
    )


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = str(text)

    text = text.replace(
        "\n",
        " "
    )

    text = text.replace(
        "\r",
        " "
    )

    text = " ".join(
        text.split()
    )

    return text.strip()


# ============================================================
# SPLIT WORDS
# ============================================================

def split_words(
    text,
    start,
    end
):

    text = clean_text(
        text
    )

    words = text.split()

    if not words:

        return []

    total_duration = (
        end - start
    )

    if total_duration <= 0:

        return []

    # --------------------------------------------------------
    # WORD WEIGHT
    # --------------------------------------------------------

    weights = []

    for word in words:

        clean = re.sub(
            r"[^\w]",
            "",
            word
        )

        weights.append(
            max(
                1,
                len(clean)
            )
        )

    total_weight = sum(
        weights
    )

    chunks = []

    current_words = []

    current_weight = 0

    current_start = start

    # --------------------------------------------------------
    # BUILD CHUNKS
    # --------------------------------------------------------

    for index, word in enumerate(
        words
    ):

        current_words.append(
            word
        )

        current_weight += (
            weights[index]
        )

        is_last = (
            index
            ==
            len(words) - 1
        )

        reached_limit = (
            len(current_words)
            >=
            MAX_WORDS_PER_CAPTION
        )

        punctuation_break = (
            word.endswith(
                (
                    ".",
                    "?",
                    "!",
                    ",",
                    ";",
                    ":"
                )
            )
            and
            len(current_words) >= 3
        )

        if (
            reached_limit
            or
            punctuation_break
            or
            is_last
        ):

            chunk_duration = (

                total_duration
                *
                current_weight
                /
                total_weight

            )

            current_end = (

                current_start
                +
                chunk_duration

            )

            current_end = min(
                current_end,
                end
            )

            # ------------------------------------------------
            # Minimum caption duration
            # ------------------------------------------------

            if (
                current_end
                -
                current_start
                <
                MIN_CAPTION_DURATION
            ):

                current_end = min(

                    end,

                    current_start
                    +
                    MIN_CAPTION_DURATION

                )

            chunks.append({

                "start":
                    current_start,

                "end":
                    current_end,

                "words":
                    current_words.copy()

            })

            current_start = current_end

            current_words = []

            current_weight = 0

    # --------------------------------------------------------
    # FORCE LAST END
    # --------------------------------------------------------

    if chunks:

        chunks[-1]["end"] = end

    return chunks


# ============================================================
# GET CLIP SEGMENTS
# ============================================================

def get_clip_segments(
    transcript,
    clip_start,
    clip_end
):

    result = []

    for seg in transcript:

        if (
            seg["end"] >= clip_start
            and
            seg["start"] <= clip_end
        ):

            result.append(
                seg
            )

    return result


# ============================================================
# BUILD CAPTIONS
# ============================================================

def build_captions(
    transcript,
    clip_start,
    clip_end
):

    segments = get_clip_segments(

        transcript,

        clip_start,

        clip_end

    )

    captions = []

    # ========================================================
    # CREATE CAPTIONS FROM SEGMENTS
    # ========================================================

    for seg in segments:

        start = max(

            seg["start"],

            clip_start

        )

        end = min(

            seg["end"],

            clip_end

        )

        if end <= start:

            continue

        chunks = split_words(

            seg["text"],

            start,

            end

        )

        for chunk in chunks:

            captions.append({

                "start":
                    chunk["start"]
                    -
                    clip_start,

                "end":
                    chunk["end"]
                    -
                    clip_start,

                "words":
                    chunk["words"]

            })

    # ========================================================
    # SORT
    # ========================================================

    captions.sort(

        key=lambda x:
        (
            x["start"],
            x["end"]
        )

    )

    # ========================================================
    # AUTO OVERLAP TRIM
    # ========================================================

    captions = resolve_caption_overlaps(
        captions
    )

    return captions


# ============================================================
# AUTO OVERLAP TRIM
# ============================================================

def resolve_caption_overlaps(
    captions
):

    if not captions:

        return []

    result = []

    overlap_count = 0

    removed_count = 0

    for caption in captions:

        current = {

            "start":
                float(
                    caption["start"]
                ),

            "end":
                float(
                    caption["end"]
                ),

            "words":
                caption["words"].copy()

        }

        # ----------------------------------------------------
        # FIRST CAPTION
        # ----------------------------------------------------

        if not result:

            result.append(
                current
            )

            continue

        previous = result[-1]

        # ----------------------------------------------------
        # OVERLAP DETECTED
        # ----------------------------------------------------

        if (
            current["start"]
            <
            previous["end"]
        ):

            overlap_count += 1

            # ------------------------------------------------
            # Potong caption sebelumnya tepat ketika
            # caption baru mulai.
            # ------------------------------------------------

            previous["end"] = (
                current["start"]
            )

            # ------------------------------------------------
            # Kalau caption sebelumnya jadi terlalu pendek,
            # hapus caption sebelumnya.
            # ------------------------------------------------

            if (
                previous["end"]
                -
                previous["start"]
                <
                MIN_OVERLAP_DURATION
            ):

                result.pop()

                removed_count += 1

        # ----------------------------------------------------
        # CURRENT CAPTION TERLALU PENDEK
        # ----------------------------------------------------

        if (
            current["end"]
            -
            current["start"]
            <
            MIN_OVERLAP_DURATION
        ):

            removed_count += 1

            continue

        result.append(
            current
        )

    # ========================================================
    # DEBUG INFO
    # ========================================================

    if overlap_count:

        print()

        print(
            f"✂️ Overlap detected : "
            f"{overlap_count}"
        )

        print(
            f"🗑️ Caption removed : "
            f"{removed_count}"
        )

        print(
            "✅ Previous captions "
            "automatically trimmed."
        )

    return result


# ============================================================
# FORMAT FLAT CAPTION
# ============================================================

def format_flat_caption(
    words
):

    lines = []

    current = []

    for word in words:

        current.append(
            word
        )

        if (
            len(current)
            >=
            MAX_WORDS_PER_LINE
        ):

            lines.append(
                " ".join(
                    current
                )
            )

            current = []

    if current:

        lines.append(
            " ".join(
                current
            )
        )

    return "\\N".join(
        lines
    )


# ============================================================
# ESCAPE ASS TEXT
# ============================================================

def escape_ass(text):

    text = str(text)

    text = text.replace(
        "\\",
        ""
    )

    text = text.replace(
        "{",
        "\\{"
    )

    text = text.replace(
        "}",
        "\\}"
    )

    return text


# ============================================================
# CREATE SRT
# ============================================================

def create_srt(
    captions,
    output_file
):

    lines = []

    for index, caption in enumerate(
        captions,
        1
    ):

        text = format_flat_caption(

            caption["words"]

        )

        lines.append(
            str(index)
        )

        lines.append(

            f"{srt_time(caption['start'])}"
            f" --> "
            f"{srt_time(caption['end'])}"

        )

        lines.append(
            text
        )

        lines.append("")

    with open(

        output_file,

        "w",

        encoding="utf-8-sig"

    ) as f:

        f.write(
            "\n".join(lines)
        )

    return len(captions)


# ============================================================
# CREATE ASS
# ============================================================

def create_ass(
    captions,
    output_file
):

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{FONT_NAME},{ASS_FONT_SIZE},{WHITE},{WHITE},{BLACK},{BLACK},-1,0,0,0,100,100,0,0,1,{OUTLINE},{SHADOW},{ALIGNMENT},40,40,{MARGIN_VERTICAL},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, Effect, Text
"""

    lines = [
        header
    ]

    for caption in captions:

        words = [

            escape_ass(word)

            for word in
            caption["words"]

        ]

        text = format_flat_caption(
            words
        )

        line = (

            "Dialogue: 0,"

            f"{ass_time(caption['start'])},"

            f"{ass_time(caption['end'])},"

            "Default,,0,0,0,"

            f"{text}"

        )

        lines.append(
            line
        )

    with open(

        output_file,

        "w",

        encoding="utf-8-sig"

    ) as f:

        f.write(
            "\n".join(lines)
        )

    return len(captions)


# ============================================================
# ESCAPE FFMPEG PATH
# ============================================================

def escape_filter_path(path):

    path = str(
        Path(path).resolve()
    )

    path = path.replace(
        "\\",
        "/"
    )

    path = path.replace(
        ":",
        "\\:"
    )

    path = path.replace(
        "'",
        "\\'"
    )

    return path


# ============================================================
# BURN ASS
# ============================================================

def burn_ass(
    input_file,
    ass_file,
    output_file
):

    subtitle_path = escape_filter_path(
        ass_file
    )

    subtitle_filter = (
        f"ass='{subtitle_path}'"
    )

    command = [

        "ffmpeg",

        "-y",

        "-i",
        str(input_file),

        "-vf",
        subtitle_filter,

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

    return (
        result.returncode == 0
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "🔥 SUBTITLE CLIPS V8.9"
    )

    print(
        "FLAT CLEAN + AUTO OVERLAP TRIM"
    )

    print("=" * 60)

    print()

    # ========================================================
    # LOAD TRANSCRIPT
    # ========================================================

    print(
        "Loading transcript..."
    )

    raw_transcript = load_json(
        TRANSCRIPT_FILE
    )

    transcript = normalize_transcript(
        raw_transcript
    )

    # ========================================================
    # LOAD CLIPS
    # ========================================================

    print(
        "Loading clips..."
    )

    clips = load_json(
        CLIPS_FILE
    )

    # ========================================================
    # DIRECTORIES
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    TEMP_SRT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    TEMP_ASS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # INFO
    # ========================================================

    print()

    print(
        f"Transcript      : "
        f"{len(transcript)} segments"
    )

    print(
        f"Clips           : "
        f"{len(clips)}"
    )

    print(
        f"ASS Font size   : "
        f"{ASS_FONT_SIZE}"
    )

    print(
        f"Margin vertical : "
        f"{MARGIN_VERTICAL}"
    )

    print(
        "Style           : FLAT WHITE"
    )

    print(
        "Highlight       : OFF"
    )

    print(
        "Position        : BOTTOM CENTER"
    )

    print(
        "Overlap fix     : AUTO TRIM"
    )

    # ========================================================
    # PROCESS
    # ========================================================

    success = 0

    failed = 0

    for index, clip in enumerate(
        clips,
        1
    ):

        start = float(
            clip["start"]
        )

        end = float(
            clip["end"]
        )

        input_file = (

            INPUT_DIR
            /
            f"short_{index:03d}.mp4"

        )

        srt_file = (

            TEMP_SRT_DIR
            /
            f"clip_{index:03d}.srt"

        )

        ass_file = (

            TEMP_ASS_DIR
            /
            f"clip_{index:03d}.ass"

        )

        output_file = (

            OUTPUT_DIR
            /
            f"final_{index:03d}.mp4"

        )

        print()

        print(
            "-" * 60
        )

        print(
            f"🎬 CLIP {index}"
        )

        print(

            f"{start:.2f}s → "
            f"{end:.2f}s"

        )

        print(
            "-" * 60
        )

        # ====================================================
        # CHECK INPUT
        # ====================================================

        if not input_file.exists():

            print(

                f"❌ Input tidak ditemukan: "
                f"{input_file}"

            )

            failed += 1

            continue

        # ====================================================
        # BUILD CAPTIONS
        # ====================================================

        captions = build_captions(

            transcript,

            start,

            end

        )

        print(

            f"📝 Captions: "
            f"{len(captions)}"

        )

        # ====================================================
        # SAVE SRT
        # ====================================================

        create_srt(

            captions,

            srt_file

        )

        print(

            f"💾 SRT → "
            f"{srt_file}"

        )

        # ====================================================
        # SAVE ASS
        # ====================================================

        create_ass(

            captions,

            ass_file

        )

        print(

            f"💾 ASS → "
            f"{ass_file}"

        )

        # ====================================================
        # RENDER
        # ====================================================

        print(
            "🔥 Rendering..."
        )

        ok = burn_ass(

            input_file,

            ass_file,

            output_file

        )

        # ====================================================
        # RESULT
        # ====================================================

        if ok:

            success += 1

            print()

            print(

                f"✅ DONE → "
                f"{output_file}"

            )

        else:

            failed += 1

            print(
                "❌ FAILED"
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 60)

    print(
        "🔥 SUBTITLE V8.9 SELESAI"
    )

    print("=" * 60)

    print()

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
        "Output → subtitled\\"
    )

    print()

    if failed:

        print(
            "⚠ Ada subtitle yang gagal."
        )

        return 1

    print(
        "✅ Semua subtitle berhasil dibuat!"
    )

    return 0


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )