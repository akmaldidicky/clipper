# ============================================================
# 🔥 CAPTION GENERATOR V1
# Final Clips → Upload Captions
# ============================================================

import json
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "analysis/final_clips.json"
)

OUTPUT_DIR = Path(
    "captions"
)


# ============================================================
# LOAD
# ============================================================

def load_final_clips():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"\nFile tidak ditemukan:\n"
            f"{INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    if not isinstance(data, list):

        raise ValueError(
            "final_clips.json harus berupa list."
        )

    return data


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    return " ".join(
        str(text)
        .split()
    ).strip()


# ============================================================
# BUILD CAPTION
# ============================================================

def build_caption(clip):

    title = clean_text(
        clip.get("title", "")
    )

    main_idea = clean_text(
        clip.get("main_idea", "")
    )

    hook = clean_text(
        clip.get("hook", "")
    )

    payoff = clean_text(
        clip.get("payoff", "")
    )

    lines = []

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if title:

        lines.append(
            title
        )

    # --------------------------------------------------------
    # SPACING
    # --------------------------------------------------------

    lines.append("")

    # --------------------------------------------------------
    # HOOK
    # --------------------------------------------------------

    if hook:

        lines.append(
            hook
        )

    # --------------------------------------------------------
    # MAIN IDEA
    # --------------------------------------------------------

    if main_idea:

        lines.append(
            main_idea
        )

    # --------------------------------------------------------
    # PAYOFF
    # --------------------------------------------------------

    if payoff:

        lines.append(
            payoff
        )

    # --------------------------------------------------------
    # CTA
    # --------------------------------------------------------

    lines.append("")

    lines.append(
        "Menurut lo gimana?"
    )

    # --------------------------------------------------------
    # HASHTAGS
    # --------------------------------------------------------

    lines.append("")

    lines.append(
        "#shorts"
    )

    return "\n".join(lines)


# ============================================================
# SAVE
# ============================================================

def save_caption(
    clip,
    index
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        OUTPUT_DIR
        /
        f"clip_{index:03d}.txt"
    )

    caption = build_caption(
        clip
    )

    output_file.write_text(
        caption,
        encoding="utf-8"
    )

    return output_file


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)

    print(
        "🔥 CLIPPER MACHINE — CAPTION GENERATOR V1"
    )

    print("=" * 70)

    clips = load_final_clips()

    print()
    print(
        f"Input clips : {len(clips)}"
    )

    print(
        f"Output dir  : {OUTPUT_DIR}"
    )

    success = 0

    for index, clip in enumerate(
        clips,
        start=1
    ):

        print()
        print(
            f"[{index}/{len(clips)}]"
        )

        print(
            f"Title : "
            f"{clip.get('title', '')}"
        )

        try:

            output_file = save_caption(
                clip,
                index
            )

            success += 1

            print(
                f"✅ Caption → "
                f"{output_file}"
            )

        except Exception as e:

            print(
                f"❌ Gagal: {e}"
            )

    print()
    print("=" * 70)

    print(
        "🔥 CAPTION GENERATOR SELESAI"
    )

    print("=" * 70)

    print(
        f"Success : {success}"
    )

    print(
        f"Output  : {OUTPUT_DIR}\\"
    )

    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()