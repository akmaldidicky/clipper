import sys
import subprocess
from pathlib import Path


MODEL = "small"
LANGUAGE = "Indonesian"


def main():
    if len(sys.argv) < 2:
        print("Usage: py transcribe.py <video.mp4>")
        sys.exit(1)

    video = Path(sys.argv[1])

    if not video.exists():
        print(f"Video tidak ditemukan: {video}")
        sys.exit(1)

    output_dir = Path("transcripts")
    output_dir.mkdir(exist_ok=True)

    print(f"\nTranscribing: {video.name}")
    print(f"Model: {MODEL}")
    print(f"Language: {LANGUAGE}\n")

    command = [
        sys.executable,
        "-m",
        "whisper",
        str(video),
        "--language",
        LANGUAGE,
        "--model",
        MODEL,
        "--output_format",
        "srt",
        "--output_dir",
        str(output_dir),
    ]

    subprocess.run(command, check=True)

    print("\n✓ Transkripsi selesai.")
    print(f"✓ Output: {output_dir}")


if __name__ == "__main__":
    main()