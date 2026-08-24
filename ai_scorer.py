import json
import sys
from pathlib import Path

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


def ask_ai(candidate):

    prompt = f"""
You are a professional short-form video editor.

You are analyzing a candidate segment from an Indonesian podcast.

Your job is NOT simply to rate the text.

Your job is to decide whether this segment should become a
YouTube Short, TikTok, or Instagram Reel.

Think like an editor who cares about RETENTION.

IMPORTANT RULES:

1. The clip should contain ONE main idea.
2. The first few seconds should make viewers want to continue watching.
3. The clip should develop an idea instead of just listing information.
4. The ending should provide a payoff, conclusion, insight, punchline,
   or memorable statement.
5. Penalize clips that contain multiple unrelated topics.
6. Penalize clips that start too early with unnecessary context.
7. Penalize clips that end before the idea is complete.
8. The clip should make sense without watching the full podcast.
9. Prefer clips around 20–60 seconds.
10. Do NOT reward a clip merely because it contains keywords.
11. Do NOT automatically prefer longer clips.
12. If the candidate is weak, say REJECT.
13. You are allowed to recommend a better start and end INSIDE
    the candidate boundaries.

Analyze this candidate.

Candidate boundaries:

START: {candidate["start"]}
END: {candidate["end"]}
DURATION: {candidate["duration"]}

TRANSCRIPT:

{candidate["text"]}


Return ONLY valid JSON.

Use exactly this structure:

{{
    "decision": "STRONG",

    "recommended_start": 0.0,
    "recommended_end": 0.0,

    "score": 0,

    "main_idea": "",

    "hook": "",

    "payoff": "",

    "title": "",

    "reason": "",

    "problems": [],

    "strengths": []
}}

DECISION must be one of:

"STRONG"
"GOOD"
"WEAK"
"REJECT"

SCORE:

90-100 = exceptional Shorts candidate
80-89  = very strong
70-79  = good
60-69  = usable but needs improvement
40-59  = weak
0-39   = reject

IMPORTANT:

recommended_start MUST be >= candidate start.

recommended_end MUST be <= candidate end.

recommended_end MUST be greater than recommended_start.

The recommended segment should preserve the complete idea.

Do not invent statements that are not present in the transcript.

This is Indonesian spoken content.
Understand slang and conversational language.

Return JSON only.
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
        timeout=300,
    )

    response.raise_for_status()

    data = response.json()

    return json.loads(data["response"])


def validate_analysis(candidate, analysis):

    candidate_start = float(candidate["start"])
    candidate_end = float(candidate["end"])

    recommended_start = float(
        analysis.get(
            "recommended_start",
            candidate_start
        )
    )

    recommended_end = float(
        analysis.get(
            "recommended_end",
            candidate_end
        )
    )

    # Keep AI inside original candidate boundaries.

    recommended_start = max(
        candidate_start,
        recommended_start
    )

    recommended_end = min(
        candidate_end,
        recommended_end
    )

    # Make sure end is after start.

    if recommended_end <= recommended_start:
        recommended_start = candidate_start
        recommended_end = candidate_end

    analysis["recommended_start"] = recommended_start
    analysis["recommended_end"] = recommended_end

    try:
        analysis["score"] = int(
            analysis.get("score", 0)
        )
    except:
        analysis["score"] = 0

    return analysis


def main():

    if len(sys.argv) < 2:

        print(
            'Usage: py ai_scorer.py '
            '"analysis\\candidates.json"'
        )

        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():

        print(
            f"❌ File tidak ditemukan: "
            f"{input_path}"
        )

        sys.exit(1)

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as f:

        candidates = json.load(f)

    print()
    print("=" * 70)
    print("CLIPPER MACHINE — AI SCORER V2")
    print("=" * 70)

    results = []

    total = len(candidates)

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

        try:

            analysis = ask_ai(candidate)

            analysis = validate_analysis(
                candidate,
                analysis
            )

            result = {
                **candidate,
                "ai_analysis": analysis
            }

            results.append(result)

            print(
                f"Decision : "
                f"{analysis.get('decision')}"
            )

            print(
                f"Score    : "
                f"{analysis.get('score')}/100"
            )

            print(
                f"Recommended: "
                f"{analysis['recommended_start']:.1f}s "
                f"→ "
                f"{analysis['recommended_end']:.1f}s"
            )

            print(
                f"Title    : "
                f"{analysis.get('title', '')}"
            )

        except Exception as e:

            print(
                f"❌ AI error: {e}"
            )

    # Sort by AI score.

    results.sort(
        key=lambda x: x[
            "ai_analysis"
        ].get("score", 0),
        reverse=True
    )

    # Assign rank.

    for rank, result in enumerate(
        results,
        start=1
    ):

        result["rank"] = rank

    # Output.

    output_dir = Path("analysis")

    output_dir.mkdir(
        exist_ok=True
    )

    output_path = (
        output_dir /
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

    print()
    print("=" * 70)
    print("TOP CLIPS")
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
            analysis.get(
                "title",
                ""
            )
        )

        print(
            analysis.get(
                "main_idea",
                ""
            )
        )

    print()
    print("=" * 70)
    print(
        f"✓ Output: {output_path}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()