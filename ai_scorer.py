# ============================================================
# 🔥 CLIPPER MACHINE — AI SCORER V4
# Editorial Scoring + Smart Trim
# ============================================================

import json
import sys
from pathlib import Path

import requests


# ============================================================
# CONFIG
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "qwen2.5:3b"

REQUEST_TIMEOUT = 120


# ============================================================
# ASK AI
# ============================================================

def ask_ai(candidate):

    prompt = f"""
Kamu adalah editor video Shorts profesional.

Kamu sedang memilih potongan terbaik dari podcast Indonesia.

Tugasmu sederhana:

Tentukan apakah kandidat ini layak dijadikan
YouTube Shorts / TikTok / Instagram Reel.

NILAI TERUTAMA:

1. HOOK
   Apakah bagian awal menarik dan membuat orang ingin lanjut menonton?

2. ONE IDEA
   Apakah clip fokus pada satu gagasan utama?

3. DEVELOPMENT
   Apakah pembicara mengembangkan gagasan tersebut?

4. PAYOFF
   Apakah ada kesimpulan, insight, punchline,
   atau pernyataan yang terasa seperti payoff?

5. STANDALONE
   Apakah clip masih masuk akal tanpa menonton podcast penuh?

6. RETENTION
   Apakah ada kemungkinan penonton bertahan sampai akhir?

PENTING:

- Jangan menilai hanya berdasarkan keyword.
- Jangan otomatis memilih clip panjang.
- Clip 15 detik boleh sangat bagus.
- Clip 30–60 detik biasanya bagus jika idenya lengkap.
- Clip sampai 180 detik tetap boleh jika memang membutuhkan waktu tersebut.
- Jangan menambahkan informasi yang tidak ada di transcript.
- Gunakan bahasa Indonesia sebagai konteks.
- Bahasa transcript boleh bercampur slang dan English.
- Jika awal clip terlalu banyak basa-basi, geser recommended_start.
- Jika akhir clip terlalu panjang atau sudah tidak relevan, geser recommended_end.
- Recommended timestamp HARUS tetap berada di dalam candidate.
- Jangan memotong bagian penting dari ide.

CANDIDATE:

START:
{candidate["start"]}

END:
{candidate["end"]}

DURATION:
{candidate["duration"]}

TRANSCRIPT:

{candidate["text"]}


BERIKAN JSON SAJA.

FORMAT:

{{
    "decision": "GOOD",
    "recommended_start": 0.0,
    "recommended_end": 0.0,
    "score": 75,
    "main_idea": "",
    "hook": "",
    "payoff": "",
    "title": "",
    "reason": "",
    "problems": [],
    "strengths": []
}}

DECISION:

STRONG
GOOD
WEAK
REJECT

SCORING:

90-100 = sangat kuat
80-89  = sangat bagus
70-79  = bagus
60-69  = masih usable
40-59  = lemah
0-39   = reject

INGAT:

Score harus mencerminkan kualitas clip sebagai SHORT.

Jangan memberikan score yang sama kepada semua kandidat
hanya karena semuanya memiliki kekurangan.

Gunakan rentang score secara realistis.

Recommended start >= candidate start.

Recommended end <= candidate end.

Recommended end > recommended start.

Return JSON ONLY.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2
            }
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    return json.loads(
        data["response"]
    )


# ============================================================
# VALIDATE AI RESULT
# ============================================================

def validate_analysis(
    candidate,
    analysis
):

    candidate_start = float(
        candidate["start"]
    )

    candidate_end = float(
        candidate["end"]
    )

    # --------------------------------------------------------
    # Recommended start
    # --------------------------------------------------------

    try:

        recommended_start = float(
            analysis.get(
                "recommended_start",
                candidate_start
            )
        )

    except:

        recommended_start = candidate_start

    # --------------------------------------------------------
    # Recommended end
    # --------------------------------------------------------

    try:

        recommended_end = float(
            analysis.get(
                "recommended_end",
                candidate_end
            )
        )

    except:

        recommended_end = candidate_end

    # --------------------------------------------------------
    # Clamp
    # --------------------------------------------------------

    recommended_start = max(
        candidate_start,
        recommended_start
    )

    recommended_start = min(
        candidate_end,
        recommended_start
    )

    recommended_end = min(
        candidate_end,
        recommended_end
    )

    recommended_end = max(
        candidate_start,
        recommended_end
    )

    # --------------------------------------------------------
    # Safety
    # --------------------------------------------------------

    if recommended_end <= recommended_start:

        recommended_start = candidate_start
        recommended_end = candidate_end

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    try:

        score = int(
            float(
                analysis.get(
                    "score",
                    0
                )
            )
        )

    except:

        score = 0

    score = max(
        0,
        min(
            100,
            score
        )
    )

    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    decision = str(
        analysis.get(
            "decision",
            ""
        )
    ).upper().strip()

    valid_decisions = {
        "STRONG",
        "GOOD",
        "WEAK",
        "REJECT"
    }

    if decision not in valid_decisions:

        if score >= 90:
            decision = "STRONG"

        elif score >= 70:
            decision = "GOOD"

        elif score >= 40:
            decision = "WEAK"

        else:
            decision = "REJECT"

    # --------------------------------------------------------
    # Store validated values
    # --------------------------------------------------------

    analysis["decision"] = decision

    analysis["score"] = score

    analysis["recommended_start"] = (
        round(
            recommended_start,
            2
        )
    )

    analysis["recommended_end"] = (
        round(
            recommended_end,
            2
        )
    )

    return analysis


# ============================================================
# FALLBACK
# ============================================================

def fallback_analysis(candidate):

    """
    Kalau Ollama timeout/error,
    candidate tetap disimpan.

    Kita kasih score rendah supaya tidak
    otomatis menang di finalization.
    """

    return {

        "decision": "WEAK",

        "recommended_start": float(
            candidate["start"]
        ),

        "recommended_end": float(
            candidate["end"]
        ),

        "score": 30,

        "main_idea": "",

        "hook": "",

        "payoff": "",

        "title": "",

        "reason": (
            "AI analysis gagal atau timeout."
        ),

        "problems": [
            "AI analysis failed"
        ],

        "strengths": []

    }


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) < 2:

        print()

        print(
            "Usage:"
        )

        print(
            'py ai_scorer.py '
            '"analysis\\candidates.json"'
        )

        sys.exit(1)

    input_path = Path(
        sys.argv[1]
    )

    if not input_path.exists():

        print()

        print(
            f"❌ File tidak ditemukan: "
            f"{input_path}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as f:

        candidates = json.load(f)

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    print()

    print("=" * 70)

    print(
        "🔥 CLIPPER MACHINE — AI SCORER V4"
    )

    print("=" * 70)

    print(
        f"Input     : {input_path}"
    )

    print(
        f"Candidates : {len(candidates)}"
    )

    print(
        f"Model      : {MODEL}"
    )

    print(
        f"Timeout    : {REQUEST_TIMEOUT}s"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    results = []

    total = len(
        candidates
    )

    success = 0
    failed = 0

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        print()

        print(
            f"[{index}/{total}] "
            f"{candidate['start']:.1f}s → "
            f"{candidate['end']:.1f}s"
        )

        print(
            f"Duration : "
            f"{candidate['duration']:.1f}s"
        )

        try:

            analysis = ask_ai(
                candidate
            )

            analysis = validate_analysis(
                candidate,
                analysis
            )

            success += 1

            print(
                f"Decision : "
                f"{analysis['decision']}"
            )

            print(
                f"Score    : "
                f"{analysis['score']}/100"
            )

            print(
                f"Recommended : "
                f"{analysis['recommended_start']:.1f}s "
                f"→ "
                f"{analysis['recommended_end']:.1f}s"
            )

            print(
                f"Title    : "
                f"{analysis.get('title', '')}"
            )

        except Exception as e:

            failed += 1

            print(
                f"⚠️ AI error: {e}"
            )

            print(
                "↳ Using fallback analysis"
            )

            analysis = fallback_analysis(
                candidate
            )

        # ----------------------------------------------------
        # BUILD RESULT
        # ----------------------------------------------------

        result = {
            **candidate,
            "ai_analysis": analysis
        }

        results.append(
            result
        )

    # ========================================================
    # SORT
    # ========================================================

    results.sort(
        key=lambda x:
        x["ai_analysis"].get(
            "score",
            0
        ),
        reverse=True
    )

    # ========================================================
    # RANK
    # ========================================================

    for rank, result in enumerate(
        results,
        start=1
    ):

        result["rank"] = rank

    # ========================================================
    # OUTPUT
    # ========================================================

    output_dir = Path(
        "analysis"
    )

    output_dir.mkdir(
        exist_ok=True
    )

    output_path = (
        output_dir
        /
        "ai_scored_candidates.json"
    )

    output_path.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # ========================================================
    # TOP CLIPS
    # ========================================================

    print()

    print("=" * 70)

    print(
        "TOP CLIPS"
    )

    print("=" * 70)

    for result in results:

        analysis = result[
            "ai_analysis"
        ]

        print()

        print(
            f"#{result['rank']} "
            f"[{analysis.get('score')}/100] "
            f"{analysis.get('decision')}"
        )

        print(
            f"{analysis['recommended_start']:.1f}s "
            f"→ "
            f"{analysis['recommended_end']:.1f}s"
        )

        print(
            f"Title : "
            f"{analysis.get('title', '')}"
        )

        print(
            f"Idea  : "
            f"{analysis.get('main_idea', '')}"
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 70)

    print(
        "🔥 AI SCORER SELESAI"
    )

    print("=" * 70)

    print(
        f"Input    : {len(candidates)}"
    )

    print(
        f"Success  : {success}"
    )

    print(
        f"Failed   : {failed}"
    )

    print(
        f"Output   : {output_path}"
    )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()