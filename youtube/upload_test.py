# ============================================================
# 🔥 YOUTUBE UPLOAD TEST V1
# Upload 1 Video - PRIVATE
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

BASE_DIR = Path(__file__).resolve().parent

VIDEO_FILE = BASE_DIR / "test.mp4"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


TITLE = "TEST UPLOAD - Clipper Machine"

DESCRIPTION = """Test upload dari Clipper Machine.

Ini adalah video test untuk memastikan YouTube API bekerja.

#Shorts #ClipperMachine
"""

TAGS = [
    "shorts",
    "clipper machine",
    "test",
]


# ============================================================
# CHECK FILE
# ============================================================

print("=" * 60)
print("🔥 YOUTUBE UPLOAD TEST V1")
print("=" * 60)
print()

if not VIDEO_FILE.exists():
    print("❌ Video tidak ditemukan!")
    print()
    print(f"Expected:")
    print(VIDEO_FILE)
    print()
    print("Taruh video test sebagai:")
    print("youtube/test.mp4")
    sys.exit(1)


if not TOKEN_FILE.exists():
    print("❌ token.json tidak ditemukan!")
    print()
    print("Jalankan auth_test.py terlebih dahulu.")
    sys.exit(1)


# ============================================================
# LOAD TOKEN
# ============================================================

print("🔑 Loading YouTube credentials...")

credentials = Credentials.from_authorized_user_file(
    TOKEN_FILE,
    SCOPES
)


# ============================================================
# REFRESH TOKEN
# ============================================================

if credentials.expired and credentials.refresh_token:
    print("🔄 Refreshing access token...")
    credentials.refresh(Request())

    TOKEN_FILE.write_text(
        credentials.to_json(),
        encoding="utf-8"
    )


if not credentials.valid:
    print("❌ Credential tidak valid!")
    print("Jalankan auth_test.py lagi.")
    sys.exit(1)


# ============================================================
# BUILD API
# ============================================================

youtube = build(
    "youtube",
    "v3",
    credentials=credentials
)


# ============================================================
# VIDEO INFO
# ============================================================

print()
print("🎬 Video:")
print(VIDEO_FILE)

print()
print("📌 Title:")
print(TITLE)

print()
print("🔒 Privacy:")
print("PRIVATE")

print()
print("🚀 Memulai upload...")
print()


# ============================================================
# REQUEST BODY
# ============================================================

body = {
    "snippet": {
        "title": TITLE,
        "description": DESCRIPTION,
        "tags": TAGS,
        "categoryId": "22",
    },
    "status": {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": False,
    },
}


# ============================================================
# MEDIA
# ============================================================

media = MediaFileUpload(
    str(VIDEO_FILE),
    chunksize=1024 * 1024,
    resumable=True,
)


# ============================================================
# UPLOAD
# ============================================================

request = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media,
)


response = None


while response is None:

    status, response = request.next_chunk()

    if status:

        progress = int(status.progress() * 100)

        print(
            f"\rUploading... {progress:3d}%",
            end="",
            flush=True
        )


print()
print()
print("=" * 60)
print("🎉 UPLOAD BERHASIL!")
print("=" * 60)
print()

video_id = response["id"]

print(f"Video ID : {video_id}")
print()
print(f"YouTube  : https://www.youtube.com/watch?v={video_id}")
print()
print("Privacy  : PRIVATE")
print()
print("🔥 YouTube API bekerja!")
print()