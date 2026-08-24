import json
import sys
from pathlib import Path

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


def ask_ai(segments):

    formatted = ""

    for i, segment in enumerate(segments):
        formatted += (
            f"[{i}] "
            f"{segment['start']:.1f}s - "
            f"{segment['end']:.1f}s\n"
            f"{segment['text']}\n\n"
        )

    prompt = f"""
You are a professional short-form video editor.

You are given consecutive transcript segments from an Indonesian podcast.

Your task is to find the strongest SHORT-FORM VIDEO IDEA.

Do NOT rewrite the transcript.

Do NOT invent information.

Choose:

1. HOOK SEGMENT
The segment that is most likely to stop someone from scrolling.

2. PAYOFF SEGMENT
The segment that gives the idea its conclusion, insight, punchline,
or memorable statement.

3. SCORE
How strong the resulting clip would be for TikTok, YouTube Shorts,
or Instagram Reels.

IMPORTANT:

- Prefer ONE clear idea.
- Prefer surprising or useful insights.
- Prefer strong statements.
- Prefer conversational moments.
- Avoid greetings and unnecessary setup.
- Avoid repetitive sentences.
- Avoid unrelated topic changes.
- A good clip is usually 15-60 seconds.
- The hook and payoff should belong to the SAME idea.
- The payoff should actually complete the idea.
- Do not select a random sentence just because it contains a keyword.

Transcript segments:

{formatted}

Return ONLY valid JSON.

Use exactly:

{{
    "hook_segment": 0,
    "payoff_segment": 0,
    "score": 0,
    "idea": "",
    "title": "",
    "reason": ""
}}

Score:

90-100 = excellent
80-89 = very strong
70-79 = good
60-69 = usable
40-59 = weak
0-39 = reject
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
        timeout=120,
    )

    response.raise_for_status()

    return json.loads(
        response.json()["response"]
    )


def main():

    if len(sys.argv) < 2:

        print(
            "Usage: py sentence_analyzer.py "
            "<transcript.json>"
        )

        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():

        print(
            f"❌ File tidak ditemukan: {input_path}"
        )

        sys.exit(1)

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as f:

        segments = json.load(f)

    print()
    print("=" * 70)
    print("CLIPPER MACHINE — SENTENCE ANALYZER V3")
    print("=" * 70)

    print(
        f"\nMenganalisis {len(segments)} segmen..."
    )

    result = ask_ai(segments)

    hook_index = int(
        result.get("hook_segment", 0)
    )

    payoff_index = int(
        result.get("payoff_segment", 0)
    )

    # Safety checks

    hook_index = max(
        0,
        min(
            hook_index,
            len(segments) - 1
        )
    )

    payoff_index = max(
        hook_index,
        min(
            payoff_index,
            len(segments) - 1
        )
    )

    hook = segments[hook_index]
    payoff = segments[payoff_index]

    start = hook["start"]
    end = payoff["end"]

    duration = end - start

    output = {
        "start": start,
        "end": end,
        "duration": duration,

        "hook_segment": hook_index,
        "payoff_segment": payoff_index,

        "hook_text": hook["text"],
        "payoff_text": payoff["text"],

        "score": result.get(
            "score",
            0
        ),

        "idea": result.get(
            "idea",
            ""
        ),

        "title": result.get(
            "title",
            ""
        ),

        "reason": result.get(
            "reason",
            ""
        )
    }

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    print(
        f"\n🎬 Clip:"
        f" {start:.1f}s → {end:.1f}s"
    )

    print(
        f"⏱ Duration:"
        f" {duration:.1f}s"
    )

    print(
        f"⭐ Score:"
        f" {output['score']}/100"
    )

    print(
        f"\n🔥 HOOK:"
        f"\n{hook['text']}"
    )

    print(
        f"\n🎯 PAYOFF:"
        f"\n{payoff['text']}"
    )

    print(
        f"\n💡 IDEA:"
        f"\n{output['idea']}"
    )

    print(
        f"\n🏷 TITLE:"
        f"\n{output['title']}"
    )

    print(
        f"\n🧠 REASON:"
        f"\n{output['reason']}"
    )

    output_dir = Path("analysis")
    output_dir.mkdir(exist_ok=True)

    output_path = (
        output_dir /
        "sentence_analysis.json"
    )

    output_path.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print(
        f"✓ Saved: {output_path}"
    )


if __name__ == "__main__":
    main()