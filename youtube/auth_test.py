# ============================================================
# 🔥 YOUTUBE OAUTH TEST V1
# ============================================================

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


# ============================================================
# CHECK CREDENTIALS
# ============================================================

if not CREDENTIALS_FILE.exists():
    print("❌ credentials.json tidak ditemukan!")
    print(f"Lokasi yang dicari:")
    print(CREDENTIALS_FILE)
    raise SystemExit(1)


# ============================================================
# OAUTH
# ============================================================

credentials = None

if TOKEN_FILE.exists():
    print("🔑 token.json ditemukan.")
    print("Mencoba menggunakan token yang sudah ada...")

    credentials = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )


# ============================================================
# REFRESH / LOGIN
# ============================================================

if credentials and credentials.expired and credentials.refresh_token:
    print("🔄 Access token expired.")
    print("Refreshing token...")

    credentials.refresh(Request())


elif not credentials or not credentials.valid:
    print()
    print("🌐 Membuka browser untuk Google OAuth...")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE,
        SCOPES
    )

    credentials = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent"
    )


# ============================================================
# SAVE TOKEN
# ============================================================

TOKEN_FILE.write_text(
    credentials.to_json(),
    encoding="utf-8"
)

print()
print("✅ OAuth berhasil!")
print(f"✅ Token disimpan:")
print(TOKEN_FILE)


# ============================================================
# BUILD YOUTUBE API
# ============================================================

youtube = build(
    "youtube",
    "v3",
    credentials=credentials
)


# ============================================================
# TEST CHANNEL
# ============================================================

print()
print("🔎 Mengecek channel YouTube...")


response = youtube.channels().list(
    part="snippet",
    mine=True
).execute()


# ============================================================
# RESULT
# ============================================================

channels = response.get("items", [])


if not channels:
    print()
    print("❌ Tidak ada channel YouTube yang ditemukan.")
    print()
    print("Pastikan akun Google yang lo authorize")
    print("memiliki channel YouTube.")
    raise SystemExit(1)


channel = channels[0]

channel_id = channel["id"]
channel_title = channel["snippet"]["title"]


print()
print("=" * 60)
print("🔥 YOUTUBE OAUTH BERHASIL")
print("=" * 60)
print()
print(f"Channel : {channel_title}")
print(f"ID      : {channel_id}")
print()
print("🎉 API YouTube siap digunakan!")
print()