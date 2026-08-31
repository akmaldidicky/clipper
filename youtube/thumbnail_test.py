# ============================================================
# 🔥 YOUTUBE THUMBNAIL TEST V1
# ============================================================

from pathlib import Path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TOKEN_FILE = BASE_DIR / "youtube" / "token.json"

THUMBNAIL_FILE = (
    BASE_DIR
    / "publish"
    / "uploaded"
    / "short_001"
    / "thumbnail.jpg"
)

VIDEO_ID = "6PbkqnX9EAI"


SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


# ============================================================
# CHECK
# ============================================================

print("=" * 70)
print("🔥 YOUTUBE THUMBNAIL TEST V1")
print("=" * 70)
print()


if not TOKEN_FILE.exists():

    print("❌ token.json tidak ditemukan!")

    sys.exit(1)


if not THUMBNAIL_FILE.exists():

    print("❌ thumbnail.jpg tidak ditemukan!")

    print()
    print(
        "Expected:"
    )

    print(
        THUMBNAIL_FILE
    )

    sys.exit(1)


if VIDEO_ID == "ISI_VIDEO_ID_DISINI":

    print(
        "❌ Isi VIDEO_ID terlebih dahulu!"
    )

    sys.exit(1)


# ============================================================
# FILE INFO
# ============================================================

file_size = (
    THUMBNAIL_FILE.stat().st_size
)


print(
    f"🖼️ Thumbnail:"
)

print(
    THUMBNAIL_FILE
)

print()

print(
    f"📦 Size:"
)

print(
    f"{file_size / 1024:.1f} KB"
)

print()

print(
    f"🎬 Video ID:"
)

print(
    VIDEO_ID
)


# ============================================================
# AUTH
# ============================================================

credentials = (
    Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )
)


if (
    credentials.expired
    and credentials.refresh_token
):

    print()
    print(
        "🔄 Refreshing token..."
    )

    credentials.refresh(
        Request()
    )


if not credentials.valid:

    print(
        "❌ Credential tidak valid!"
    )

    sys.exit(1)


# ============================================================
# API
# ============================================================

youtube = build(
    "youtube",
    "v3",
    credentials=credentials
)


# ============================================================
# UPLOAD THUMBNAIL
# ============================================================

print()
print(
    "🚀 Uploading thumbnail..."
)

print()


try:

    media = MediaFileUpload(

        str(
            THUMBNAIL_FILE
        ),

        mimetype="image/jpeg"
    )


    response = (
        youtube
        .thumbnails()
        .set(

            videoId=VIDEO_ID,

            media_body=media

        )
        .execute()
    )


    print()
    print("=" * 70)
    print("🎉 THUMBNAIL BERHASIL!")
    print("=" * 70)
    print()

    print(
        response
    )

    print()

    print(
        "Cek video YouTube lo."
    )


except Exception as e:

    print()
    print("=" * 70)
    print("❌ THUMBNAIL GAGAL")
    print("=" * 70)
    print()

    print(
        repr(e)
    )

    print()

    import traceback

    traceback.print_exc()