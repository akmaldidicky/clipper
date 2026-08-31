import re
import json
import sys
from pathlib import Path


def timestamp_to_seconds(timestamp):
    """
    Convert:
    00:01:23,450
    menjadi:
    83.45
    """

    hours, minutes, seconds, milliseconds = re.split(
        r"[:,]",
        timestamp
    )

    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(milliseconds) / 1000
    )


def parse_srt(srt_path):
    content = srt_path.read_text(encoding="utf-8-sig")

    blocks = re.split(r"\n\s*\n", content.strip())

    segments = []

    for block in blocks:
        lines = block.splitlines()

        if len(lines) < 3:
            continue

        timestamp_line = lines[1]

        match = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*"
            r"(\d{2}:\d{2}:\d{2},\d{3})",
            timestamp_line
        )

        if not match:
            continue

        start = timestamp_to_seconds(match.group(1))
        end = timestamp_to_seconds(match.group(2))

        text = " ".join(lines[2:]).strip()

        segments.append({
            "start": start,
            "end": end,
            "text": text
        })

    return segments


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print('py parse_srt.py "transcripts\\video.srt"')
        sys.exit(1)

    srt_path = Path(sys.argv[1])

    if not srt_path.exists():
        print(f"❌ File tidak ditemukan: {srt_path}")
        sys.exit(1)

    segments = parse_srt(srt_path)

    output_dir = Path("analysis")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "transcript.json"

    output_file.write_text(
        json.dumps(
            segments,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("=" * 60)
    print("SRT PARSER")
    print("=" * 60)
    print(f"Segments : {len(segments)}")
    print(f"Output   : {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()