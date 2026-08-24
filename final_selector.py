import sys
import json
import requests
from pathlib import Path


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


def ask_ai(candidates):

    candidate_text = ""

    for i, candidate in enumerate(candidates, 1):
        candidate_text += f"""
CANDIDATE {i}
Start: {candidate["start"]}s
End: {candidate["end"]}s
Score: {candidate.get("score", 0)}

Transcript:
{candidate["text"]}

---
"""

    prompt = f"""
Kamu adalah editor video Shorts.

Pilih maksimal 3 kandidat TERBAIK dari daftar berikut.

Kriteria:
- Punya hook yang menarik
- Punya satu ide utama yang jelas
- Bisa dipahami tanpa menonton podcast lengkap
- Punya payoff atau kesimpulan
- Hindari filler dan percakapan yang tidak penting
- Ideal duration 15-45 detik
- Jangan mengarang ucapan
- Jangan mengubah transcript
- Pilih berdasarkan kandidat yang tersedia
- Jangan membuat timestamp di luar start/end kandidat

{candidate_text}

Output JSON SAJA dengan format:

{{
  "selected": [
    {{
      "candidate": 1,
      "start": 0,
      "end": 0,
      "title": "",
      "reason": ""
    }}
  ]
}}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1
            }
        },
        timeout=300
    )

    response.raise_for_status()

    data = response.json()

    return json.loads(data["response"])


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print("py final_selector.py analysis\\ai_scored_candidates.json")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"❌ File tidak ditemukan: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    # Untuk testing: maksimal 6 kandidat
    candidates = candidates[:6]

    print(f"\n🔥 Selecting from {len(candidates)} candidates...")
    print("🤖 Sending ONE request to Qwen...\n")

    try:

        result = ask_ai(candidates)

    except Exception as e:

        print(f"❌ AI error: {e}")
        sys.exit(1)

    selected = result.get("selected", [])

    valid_results = []

    for item in selected:

        candidate_number = item.get("candidate")

        if not isinstance(candidate_number, int):
            continue

        if candidate_number < 1 or candidate_number > len(candidates):
            continue

        original = candidates[candidate_number - 1]

        start = float(item.get("start", original["start"]))
        end = float(item.get("end", original["end"]))

        # Pastikan timestamp masih di dalam kandidat
        start = max(start, float(original["start"]))
        end = min(end, float(original["end"]))

        if end <= start:
            continue

        valid_results.append({
            "start": start,
            "end": end,
            "title": item.get("title", ""),
            "reason": item.get("reason", ""),
            "source_candidate": candidate_number,
            "original_start": original["start"],
            "original_end": original["end"],
            "text": original["text"]
        })

    output_file = Path("analysis/final_clips.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            valid_results,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("✓ Selection selesai\n")

    for i, clip in enumerate(valid_results, 1):

        print(
            f"[{i}] "
            f"{clip['start']}s → {clip['end']}s"
        )

        print(f"    🎯 {clip['title']}")
        print(f"    💡 {clip['reason']}")
        print()

    print(f"✓ Output: {output_file}")


if __name__ == "__main__":
    main()