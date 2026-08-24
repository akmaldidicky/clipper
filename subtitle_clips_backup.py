# ============================================================
# 🔥 SUBTITLE CLIPS V8.6.3
# Shorts Subtitle + Safe Keyword Highlight
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
# SUBTITLE CONFIG
# ============================================================

MAX_WORDS_PER_CAPTION = 6
MAX_WORDS_PER_LINE = 3

MIN_CAPTION_DURATION = 0.75


# ============================================================
# VISUAL STYLE
# ============================================================

FONT_NAME = "Arial"

# 🔒 LOCKED
FONT_SIZE = 18
ASS_FONT_SIZE = 72

OUTLINE = 4
SHADOW = 2


# ============================================================
# POSITION
# ============================================================

ALIGNMENT = 2

# 🔒 LOCKED
MARGIN_VERTICAL = 360


# ============================================================
# COLORS
# ============================================================

WHITE = "&H00FFFFFF&"

YELLOW = "&H0000FFFF&"

BLACK = "&H00000000&"


# ============================================================
# IMPORTANT WORDS
# ============================================================

IMPORTANT_WORDS = {
    "berpikir",
    "berpikirnya",
    "kritis",
    "masalah",
    "penting",
    "belajar",
    "buku",
    "hidup",
    "sukses",
    "gagal",
    "manusia",
    "pikiran",
    "pengetahuan",
    "kesalahan",
    "kebiasaan",
    "perubahan",
    "tujuan",
    "alasan",
    "kenapa",
    "mengapa",
    "rahasia",
    "disiplin",
    "curiosity",
    "critical",
    "thinking",
}


# ============================================================
# STOPWORDS
# ============================================================

STOPWORDS = {
    "yang",
    "dan",
    "atau",
    "untuk",
    "dengan",
    "dari",
    "ini",
    "itu",
    "kita",
    "kami",
    "mereka",
    "dia",
    "saya",
    "aku",
    "ada",
    "akan",
    "jadi",
    "juga",
    "sudah",
    "belum",
    "bisa",
    "harus",
    "lebih",
    "sangat",
    "karena",
    "kalau",
    "dalam",
    "pada",
    "seperti",
    "tentang",
    "adalah",
    "sebuah",
    "suatu",
    "pun",
    "lah",
    "nya",
    "ya",
    "nggak",
    "tidak",
    "bukan",
    "ke",
    "di",
}


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
                "Transcript tidak punya "
                "'segments'."
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
# SRT TIME
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


# ============================================================
# ASS TIME
# ============================================================

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

    text = text.replace(
        "\n",
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
            >= MAX_WORDS_PER_CAPTION
        )

        punctuation_break = (
            word.endswith(
                (
                    ".",
                    "?",
                    "!"
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

    if chunks:

        chunks[-1]["end"] = end

    return chunks


# ============================================================
# FORMAT NORMAL CAPTION
# ============================================================

def format_caption(words):

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
                " ".join(current)
            )

            current = []

    if current:

        lines.append(
            " ".join(current)
        )

    return "\\N".join(
        lines
    )


# ============================================================
# FIND KEYWORDS
# ============================================================

def find_keywords(words):

    candidates = []

    for word in words:

        clean = re.sub(
            r"[^\w]",
            "",
            word.lower()
        )

        if not clean:
            continue

        if clean in STOPWORDS:
            continue

        score = 0

        if clean in IMPORTANT_WORDS:

            score += 10

        if len(clean) >= 8:

            score += 2

        elif len(clean) >= 6:

            score += 1

        if score > 0:

            candidates.append(
                (
                    score,
                    clean
                )
            )

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    keywords = set()

    for score, word in candidates:

        keywords.add(
            word
        )

        if len(keywords) >= 2:

            break

    return keywords


# ============================================================
# ESCAPE ASS
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
# FORMAT HIGHLIGHT CAPTION
# ============================================================

def format_highlight_caption(words):

    keywords = find_keywords(
        words
    )

    formatted = []

    for word in words:

        clean = re.sub(
            r"[^\w]",
            "",
            word.lower()
        )

        safe = escape_ass(
            word
        )

        if clean in keywords:

            safe = (
                "{\\c"
                + YELLOW
                + "}"
                + safe
                + "{\\c"
                + WHITE
                + "}"
            )

        formatted.append(
            safe
        )

    lines = []

    current = []

    for word in formatted:

        current.append(
            word
        )

        if (
            len(current)
            >=
            MAX_WORDS_PER_LINE
        ):

            lines.append(
                " ".join(current)
            )

            current = []

    if current:

        lines.append(
            " ".join(current)
        )

    return "\\N".join(
        lines
    )


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

            local_start = (
                chunk["start"]
                -
                clip_start
            )

            local_end = (
                chunk["end"]
                -
                clip_start
            )

            captions.append({

                "start":
                    local_start,

                "end":
                    local_end,

                "words":
                    chunk["words"]

            })

    return captions


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

        text = format_caption(
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

        text = format_highlight_caption(
            caption["words"]
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
# BURN SRT
# ============================================================

def burn_srt(
    input_file,
    srt_file,
    output_file
):

    subtitle_path = escape_filter_path(
        srt_file
    )

    force_style = (
        f"FontName={FONT_NAME},"
        f"FontSize={FONT_SIZE},"
        f"Bold=1,"
        f"PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,"
        f"Outline={OUTLINE},"
        f"Shadow={SHADOW},"
        f"Alignment={ALIGNMENT},"
        f"MarginV={MARGIN_VERTICAL}"
    )

    subtitle_filter = (
        f"subtitles='{subtitle_path}'"
        f":force_style='{force_style}'"
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
        "🔥 SUBTITLE CLIPS V8.6.3"
    )
    print(
        "SHORTS + KEYWORD HIGHLIGHT"
    )
    print("=" * 60)

    print()

    # ========================================================
    # LOAD
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
        f"Transcript     : "
        f"{len(transcript)} segments"
    )

    print(
        f"Clips          : "
        f"{len(clips)}"
    )

    print(
        f"Font size      : "
        f"{FONT_SIZE}"
    )

    print(
        f"Margin bottom  : "
        f"{MARGIN_VERTICAL}px"
    )

    print(
        "Highlight      : ON"
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

        print("-" * 60)

        print(
            f"🎬 CLIP {index}"
        )

        print(
            f"{start:.2f}s → "
            f"{end:.2f}s"
        )

        print("-" * 60)

        # ====================================================
        # INPUT
        # ====================================================

        if not input_file.exists():

            print(
                f"❌ Input tidak ditemukan: "
                f"{input_file}"
            )

            failed += 1

            continue

        # ====================================================
        # CAPTIONS
        # ====================================================

        captions = build_captions(
            transcript,
            start,
            end
        )

        # ====================================================
        # CREATE SRT
        # ====================================================

        srt_count = create_srt(
            captions,
            srt_file
        )

        print(
            f"📝 SRT captions : "
            f"{srt_count}"
        )

        # ====================================================
        # CREATE ASS
        # ====================================================

        ass_count = create_ass(
            captions,
            ass_file
        )

        print(
            f"🎨 ASS captions : "
            f"{ass_count}"
        )

        # ====================================================
        # TRY ASS
        # ====================================================

        print(
            "🔥 Rendering highlight..."
        )

        ok = burn_ass(
            input_file,
            ass_file,
            output_file
        )

        # ====================================================
        # FALLBACK
        # ====================================================

        if not ok:

            print(
                "⚠️ Highlight gagal."
            )

            print(
                "↩️ Fallback ke SRT normal..."
            )

            ok = burn_srt(
                input_file,
                srt_file,
                output_file
            )

        # ====================================================
        # RESULT
        # ====================================================

        if ok:

            success += 1

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
        "🔥 SUBTITLE V8.6.3 SELESAI"
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
        "Output:"
    )

    print(
        "subtitled\\"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()