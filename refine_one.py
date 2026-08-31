import sys
import json
import requests
from pathlib import Path


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

MIN_DURATION = 15
MAX_DURATION = 45


def ask_ai(candidate):

    start = candidate["start"]
    end = candidate["end"]
    text = candidate["text"]

    prompt = f"""
Kamu adalah editor video podcast untuk YouTube Shorts/TikTok/Reels.

Tugasmu BUKAN membuat ulang ucapan pembicara.

Tugasmu adalah mencari BAGIAN TERBAIK dari kandidat podcast berikut.

ATURAN PENTING:

1. Jangan mengubah kata-kata pembicara.
2. Jangan membuat kalimat baru.
3. Jangan mengarang informasi.
4. Recommended start dan end HARUS berada di antara {start} dan {end}.
5. Durasi ideal 15-45 detik.
6. Cari satu ide utama saja.
7. Harus punya hook yang menarik.
8. Harus punya payoff atau kesimpulan.
9. Buang filler dan bagian yang tidak penting.
10. Jangan memilih bagian hanya karena panjang.
11. Kalau awal kandidat terlalu lambat, mulai lebih tengah.
12. Kalau akhir kandidat masih menggantung, potong sebelum bagian tersebut.
13. Prioritaskan bagian yang bisa dipahami tanpa menonton podcast lengkap.
14. Jangan membahas kualitas audio/video.
15. Output HARUS JSON valid.

TRANSKRIP:

{text}

Kembalikan JSON dengan format:

{{
  "recommended_start": 0,
  "recommended_end": 0,
  "hook_text": "",
  "core_text": "",
  "payoff_text": "",
  "score": 0,
  "idea": "",
  "title": "",
  "reason": ""
}}

Score 0-100.

Sekarang pilih bagian terbaik.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=600,
    )

    response.raise_for_status()

    data = response.json()

    raw = data.get("response", "")

    return json.loads(raw)


def main():

    if len(sys.argv) < 3:

        print(
            "Usage:\n"
            "py refine_one.py "
            "<ai_scored_candidates.json> "
            "<candidate_number>"
        )

        print()
        print("Example:")
        print(
            "py refine_one.py "
            "analysis\\ai_scored_candidates.json 1"
        )

        sys.exit(1)

    input_file = Path(sys.argv[1])

    try:
        candidate_number = int(sys.argv[2])
    except ValueError:

        print("❌ Candidate number harus angka.")
        sys.exit(1)

    if not input_file.exists():

        print(
            f"❌ File tidak ditemukan: {input_file}"
        )

        sys.exit(1)

    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as f:

        candidates = json.load(f)

    if candidate_number < 1 or candidate_number > len(candidates):

        print(
            f"❌ Candidate harus antara "
            f"1 dan {len(candidates)}"
        )

        sys.exit(1)

    candidate = candidates[candidate_number - 1]

    print()
    print("=" * 60)
    print("🔥 REFINE ONE CANDIDATE")
    print("=" * 60)

    print(
        f"Candidate : #{candidate_number}"
    )

    print(
        f"Range     : "
        f"{candidate['start']}s → "
        f"{candidate['end']}s"
    )

    print(
        f"Duration  : "
        f"{candidate['end'] - candidate['start']:.1f}s"
    )

    print()
    print("🤖 Asking Ollama...")
    print()

    try:

        result = ask_ai(candidate)

    except Exception as e:

        print(
            f"❌ AI error: {e}"
        )

        sys.exit(1)

    # ========================================================
    # VALIDATE
    # ========================================================

    rec_start = float(
        result["recommended_start"]
    )

    rec_end = float(
        result["recommended_end"]
    )

    duration = rec_end - rec_start

    if rec_start < candidate["start"]:
        print("⚠️ Start AI keluar dari range. Diperbaiki.")
        rec_start = candidate["start"]

    if rec_end > candidate["end"]:
        print("⚠️ End AI keluar dari range. Diperbaiki.")
        rec_end = candidate["end"]

    duration = rec_end - rec_start

    if duration < MIN_DURATION:

        print(
            f"⚠️ Durasi terlalu pendek: "
            f"{duration:.1f}s"
        )

    if duration > MAX_DURATION:

        print(
            f"⚠️ Durasi terlalu panjang: "
            f"{duration:.1f}s"
        )

    result["recommended_start"] = rec_start
    result["recommended_end"] = rec_end

    result["original_start"] = candidate["start"]
    result["original_end"] = candidate["end"]

    result["original_text"] = candidate["text"]

    # ========================================================
    # SAVE
    # ========================================================

    output_dir = input_file.parent

    output_file = (
        output_dir /
        "refined_one.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    # ========================================================
    # RESULT
    # ========================================================

    print("=" * 60)
    print("✅ REFINE SELESAI")
    print("=" * 60)

    print()
    print(
        f"Original : "
        f"{candidate['start']:.1f}s → "
        f"{candidate['end']:.1f}s"
    )

    print(
        f"Recommended : "
        f"{rec_start:.1f}s → "
        f"{rec_end:.1f}s"
    )

    print(
        f"Duration : "
        f"{duration:.1f}s"
    )

    print(
        f"Score : "
        f"{result.get('score', 0)}"
    )

    print()
    print(
        f"🎯 Title: "
        f"{result.get('title', '')}"
    )

    print()
    print(
        f"🪝 Hook:\n"
        f"{result.get('hook_text', '')}"
    )

    print()
    print(
        f"💡 Core:\n"
        f"{result.get('core_text', '')}"
    )

    print()
    print(
        f"🎯 Payoff:\n"
        f"{result.get('payoff_text', '')}"
    )

    print()
    print(
        f"📄 Output: {output_file}"
    )


if __name__ == "__main__":
    main()