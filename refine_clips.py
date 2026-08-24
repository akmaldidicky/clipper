# ============================================================
# 🔥 REFINE CLIPS V8.1
# Segment-safe / Whisper-compatible
# ============================================================

import json
import requests
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

MODEL = "qwen2.5:3b"

MIN_DURATION = 15
MAX_DURATION = 180

INPUT_CANDIDATES = Path("analysis/unique_candidates.json")
INPUT_TRANSCRIPT = Path("analysis/transcript.json")
OUTPUT_FILE = Path("analysis/refined_clips.json")

OLLAMA_URL = "http://localhost:11434/api/generate"


# ============================================================
# LOAD JSON
# ============================================================

def load_json(path):

    if not path.exists():
        raise FileNotFoundError(
            f"File tidak ditemukan: {path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# NORMALIZE TRANSCRIPT
# ============================================================

def normalize_transcript(raw_transcript):

    # --------------------------------------------------------
    # Kalau JSON langsung berupa list
    # --------------------------------------------------------

    if isinstance(raw_transcript, list):
        segments = raw_transcript

    # --------------------------------------------------------
    # Kalau JSON berupa object
    # --------------------------------------------------------

    elif isinstance(raw_transcript, dict):

        # format umum Whisper JSON
        if "segments" in raw_transcript:
            segments = raw_transcript["segments"]

        else:
            raise ValueError(
                "Transcript JSON tidak punya key 'segments'."
            )

    else:

        raise ValueError(
            "Format transcript JSON tidak dikenal."
        )

    # --------------------------------------------------------
    # Normalisasi
    # --------------------------------------------------------

    normalized = []

    for index, seg in enumerate(segments):

        if not isinstance(seg, dict):
            continue

        if "start" not in seg:
            continue

        if "end" not in seg:
            continue

        if "text" not in seg:
            continue

        normalized.append({
            "id": index,
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": str(seg["text"]).strip()
        })

    if not normalized:

        raise ValueError(
            "Tidak ada segment valid di transcript."
        )

    return normalized


# ============================================================
# OLLAMA
# ============================================================

def ask_ai(prompt):

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError:

        raise RuntimeError(
            "Ollama tidak bisa dihubungi.\n"
            "Pastikan Ollama sedang running."
        )

    except requests.exceptions.Timeout:

        raise RuntimeError(
            "Request ke Ollama timeout."
        )

    data = response.json()

    if "response" not in data:

        raise RuntimeError(
            f"Response Ollama tidak valid:\n{data}"
        )

    return data["response"]


# ============================================================
# EXTRACT JSON
# ============================================================

def extract_json(text):

    if not text:
        return None

    text = text.strip()

    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:
        return json.loads(text)

    except Exception:
        pass

    # --------------------------------------------------------
    # Cari JSON object
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:

        candidate = text[start:end + 1]

        try:
            return json.loads(candidate)

        except Exception:
            pass

    return None


# ============================================================
# BUILD TRANSCRIPT CONTEXT
# ============================================================

def build_transcript_context(segments):

    lines = []

    for seg in segments:

        idx = seg["id"]

        start = seg["start"]
        end = seg["end"]

        text = seg["text"]

        lines.append(
            f"[SEGMENT {idx}] "
            f"{start:.2f}s → {end:.2f}s\n"
            f"{text}"
        )

    return "\n".join(lines)


# ============================================================
# GET RELEVANT SEGMENTS
# ============================================================

def get_relevant_segments(
    transcript,
    candidate_start,
    candidate_end
):

    relevant = []

    for seg in transcript:

        # overlap check
        if (
            seg["end"] >= candidate_start
            and
            seg["start"] <= candidate_end
        ):

            relevant.append(seg)

    return relevant


# ============================================================
# REFINE ONE CANDIDATE
# ============================================================

def refine_candidate(
    candidate,
    transcript
):

    candidate_start = float(
        candidate.get("start", 0)
    )

    candidate_end = float(
        candidate.get("end", 0)
    )

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if candidate_end <= candidate_start:

        print("❌ Candidate timestamp invalid")

        return None

    # --------------------------------------------------------
    # Get relevant transcript
    # --------------------------------------------------------

    relevant = get_relevant_segments(
        transcript,
        candidate_start,
        candidate_end
    )

    if not relevant:

        print("❌ Tidak ada transcript yang overlap")

        return None

    # --------------------------------------------------------
    # Transcript context
    # --------------------------------------------------------

    context = build_transcript_context(
        relevant
    )

    first_segment = relevant[0]["id"]
    last_segment = relevant[-1]["id"]

    # --------------------------------------------------------
    # Candidate metadata
    # --------------------------------------------------------

    title = candidate.get(
        "title",
        ""
    )

    hook = candidate.get(
        "hook",
        ""
    )

    score = candidate.get(
        "score",
        candidate.get(
            "total_score",
            ""
        )
    )

    # --------------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are refining a short-form video clip.

Your job is SIMPLE:

Choose the best start and end SEGMENT from the transcript.

Do NOT invent timestamps.

Do NOT invent segment IDs.

The final clip should contain a COMPLETE thought.

The clip should ideally:

- have a strong hook
- contain useful or interesting information
- make sense by itself
- avoid unnecessary introduction
- avoid ending before the speaker finishes the idea
- avoid cutting important sentences
- feel natural when watched as a standalone short

IMPORTANT:

Minimum duration: {MIN_DURATION} seconds
Maximum duration: {MAX_DURATION} seconds

Candidate:

Start:
{candidate_start:.2f}

End:
{candidate_end:.2f}

Title:
{title}

Hook:
{hook}

Score:
{score}

Available segment range:

{first_segment} → {last_segment}

Transcript:

{context}

Choose start_segment and end_segment.

Return ONLY JSON.

Example:

{{
  "start_segment": 2,
  "end_segment": 8,
  "reason": "The clip contains a complete idea and ends naturally."
}}
"""

    # --------------------------------------------------------
    # ASK AI
    # --------------------------------------------------------

    try:

        raw = ask_ai(prompt)

    except Exception as e:

        print(f"❌ AI ERROR: {e}")

        return None

    print("\n🤖 RAW AI RESPONSE:")

    print(raw)

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    result = extract_json(raw)

    if not result:

        print(
            "❌ AI tidak menghasilkan JSON valid"
        )

        return None

    # --------------------------------------------------------
    # Read segment IDs
    # --------------------------------------------------------

    try:

        start_id = int(
            result["start_segment"]
        )

        end_id = int(
            result["end_segment"]
        )

    except Exception:

        print(
            "❌ start_segment/end_segment invalid"
        )

        return None

    # --------------------------------------------------------
    # Order validation
    # --------------------------------------------------------

    if start_id > end_id:

        print(
            "❌ start_segment lebih besar "
            "dari end_segment"
        )

        return None

    # --------------------------------------------------------
    # Make sure IDs exist
    # --------------------------------------------------------

    valid_ids = {
        seg["id"]
        for seg in relevant
    }

    if start_id not in valid_ids:

        print(
            f"❌ start_segment {start_id} "
            f"tidak ada"
        )

        return None

    if end_id not in valid_ids:

        print(
            f"❌ end_segment {end_id} "
            f"tidak ada"
        )

        return None

    # --------------------------------------------------------
    # Select segments
    # --------------------------------------------------------

    selected = [

        seg

        for seg in relevant

        if (
            start_id
            <= seg["id"]
            <= end_id
        )

    ]

    if not selected:

        print(
            "❌ Tidak ada segment terpilih"
        )

        return None

    # --------------------------------------------------------
    # Calculate timestamp
    # --------------------------------------------------------

    start = selected[0]["start"]

    end = selected[-1]["end"]

    duration = end - start

    # --------------------------------------------------------
    # Duration validation
    # --------------------------------------------------------

    if duration < MIN_DURATION:

        print(
            f"⚠️ Clip terlalu pendek: "
            f"{duration:.1f}s"
        )

        return None

    if duration > MAX_DURATION:

        print(
            f"⚠️ Clip terlalu panjang: "
            f"{duration:.1f}s"
        )

        return None

    # --------------------------------------------------------
    # Candidate boundary tolerance
    # --------------------------------------------------------

    tolerance = 10

    if start < candidate_start - tolerance:

        print(
            "⚠️ Start terlalu jauh "
            "dari candidate"
        )

        return None

    if end > candidate_end + tolerance:

        print(
            "⚠️ End terlalu jauh "
            "dari candidate"
        )

        return None

    # --------------------------------------------------------
    # Build result
    # --------------------------------------------------------

    refined = {

        "start": round(
            start,
            2
        ),

        "end": round(
            end,
            2
        ),

        "duration": round(
            duration,
            2
        ),

        "start_segment": start_id,

        "end_segment": end_id,

        "title": title,

        "hook": hook,

        "score": score,

        "reason": result.get(
            "reason",
            ""
        )

    }

    return refined


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "🔥 REFINE CLIPS V8.1"
    )

    print("=" * 60)

    print()

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    print(
        f"Loading candidates..."
    )

    raw_candidates = load_json(
        INPUT_CANDIDATES
    )

    print(
        f"Loading transcript..."
    )

    raw_transcript = load_json(
        INPUT_TRANSCRIPT
    )

    # --------------------------------------------------------
    # Normalize transcript
    # --------------------------------------------------------

    transcript = normalize_transcript(
        raw_transcript
    )

    # --------------------------------------------------------
    # Candidates
    # --------------------------------------------------------

    if not isinstance(
        raw_candidates,
        list
    ):

        raise ValueError(
            "unique_candidates.json "
            "harus berupa list."
        )

    candidates = raw_candidates

    # --------------------------------------------------------
    # Info
    # --------------------------------------------------------

    print()

    print(
        f"Candidates : {len(candidates)}"
    )

    print(
        f"Transcript : {len(transcript)} segments"
    )

    print(
        f"Model      : {MODEL}"
    )

    print(
        f"Duration   : "
        f"{MIN_DURATION}s → "
        f"{MAX_DURATION}s"
    )

    print()

    # --------------------------------------------------------
    # Refine
    # --------------------------------------------------------

    refined = []

    for i, candidate in enumerate(
        candidates,
        1
    ):

        candidate_start = float(
            candidate.get(
                "start",
                0
            )
        )

        candidate_end = float(
            candidate.get(
                "end",
                0
            )
        )

        print(
            f"[{i}/{len(candidates)}] "
            f"{candidate_start:.1f}s → "
            f"{candidate_end:.1f}s"
        )

        result = refine_candidate(
            candidate,
            transcript
        )

        if result:

            refined.append(
                result
            )

            print()

            print(
                f"✅ ACCEPTED"
            )

            print(
                f"   Start    : "
                f"{result['start']:.2f}s"
            )

            print(
                f"   End      : "
                f"{result['end']:.2f}s"
            )

            print(
                f"   Duration : "
                f"{result['duration']:.2f}s"
            )

            print(
                f"   Segment  : "
                f"{result['start_segment']}"
                f" → "
                f"{result['end_segment']}"
            )

        else:

            print()

            print(
                "❌ REJECTED"
            )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            refined,
            f,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()

    print("=" * 60)

    print(
        "🔥 REFINE SELESAI"
    )

    print("=" * 60)

    print(
        f"Input candidates : "
        f"{len(candidates)}"
    )

    print(
        f"Accepted         : "
        f"{len(refined)}"
    )

    print(
        f"Rejected         : "
        f"{len(candidates) - len(refined)}"
    )

    print()

    print(
        f"Saved → "
        f"{OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()