# ============================================================
# 🔥 YOUTUBE PUBLISHER V2
# Batch Upload → YouTube
# ============================================================

from pathlib import Path
import json
import shutil
import sys
import time
import gc

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

YOUTUBE_DIR = BASE_DIR / "youtube"

QUEUE_DIR = BASE_DIR / "publish" / "queue"
UPLOADED_DIR = BASE_DIR / "publish" / "uploaded"
FAILED_DIR = BASE_DIR / "publish" / "failed"

TOKEN_FILE = YOUTUBE_DIR / "token.json"


# ============================================================
# YOUTUBE API
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


# ============================================================
# PUBLISH SETTINGS
# ============================================================

# Untuk batch pertama:
# private = aman
# unlisted = bisa dibuka dengan link
# public = langsung tayang

PRIVACY_STATUS = "public"


# ============================================================
# CATEGORY
# ============================================================

# 22 = People & Blogs
#
# Bisa kita ubah nanti kalau diperlukan.

CATEGORY_ID = "22"


# ============================================================
# HELPERS
# ============================================================

def print_header():

    print()
    print("=" * 70)
    print("🔥 YOUTUBE PUBLISHER V2")
    print("=" * 70)
    print()


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )
# ============================================================
# SCHEDULE HELPER
# ============================================================

def get_publish_settings(metadata):

    publish_at = metadata.get(
        "publish_at"
    )


    # Tidak ada jadwal
    if not publish_at:

        return {
            "privacyStatus": "public"
        }


    # Ada jadwal
    return {
        "privacyStatus": "private",
        "publishAt": publish_at
    }
    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def safe_archive(
    source,
    destination
):

    """
    Windows-safe:

    COPY
      ↓
    VERIFY
      ↓
    DELETE SOURCE
    """

    if destination.exists():

        shutil.rmtree(
            destination
        )


    print()
    print(
        "📦 Archiving..."
    )


    shutil.copytree(
        source,
        destination
    )


    gc.collect()

    time.sleep(2)


    shutil.rmtree(
        source
    )


    print(
        "✅ Archived."
    )


def safe_failed(
    source,
    destination
):

    """
    Windows-safe failed archive.
    """

    if destination.exists():

        shutil.rmtree(
            destination
        )


    try:

        shutil.copytree(
            source,
            destination
        )


        gc.collect()

        time.sleep(1)


        shutil.rmtree(
            source
        )


    except Exception as e:

        print()
        print(
            "⚠️ Gagal memindahkan "
            "ke failed/"
        )

        print(e)


# ============================================================
# DIRECTORIES
# ============================================================

QUEUE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

UPLOADED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FAILED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# HEADER
# ============================================================

print_header()


# ============================================================
# TOKEN
# ============================================================

if not TOKEN_FILE.exists():

    print(
        "❌ token.json tidak ditemukan!"
    )

    print()

    print(
        "Jalankan:"
    )

    print(
        "py youtube\\auth_test.py"
    )

    sys.exit(1)


print(
    "🔑 Loading YouTube credentials..."
)


credentials = (
    Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )
)


# ============================================================
# REFRESH TOKEN
# ============================================================

if (
    credentials.expired
    and credentials.refresh_token
):

    print(
        "🔄 Refreshing access token..."
    )

    credentials.refresh(
        Request()
    )


    TOKEN_FILE.write_text(
        credentials.to_json(),
        encoding="utf-8"
    )


if not credentials.valid:

    print()
    print(
        "❌ Credentials tidak valid!"
    )

    print()

    print(
        "Jalankan:"
    )

    print(
        "py youtube\\auth_test.py"
    )

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
# FIND QUEUE
# ============================================================

jobs = sorted(
    [
        p
        for p in QUEUE_DIR.iterdir()
        if p.is_dir()
    ]
)


print()
print(
    f"📦 Queue folder : {QUEUE_DIR}"
)

print(
    f"📦 Videos found : {len(jobs)}"
)

print(
    f"🔒 Privacy      : {PRIVACY_STATUS}"
)

print()


# ============================================================
# EMPTY QUEUE
# ============================================================

if not jobs:

    print(
        "⚠️ Queue kosong."
    )

    print()

    print(
        "Masukkan folder video ke:"
    )

    print(
        QUEUE_DIR
    )

    sys.exit(0)


# ============================================================
# CONFIRM
# ============================================================

print(
    "📋 Queue:"
)

for i, job in enumerate(
    jobs,
    start=1
):

    print(
        f"   {i}. {job.name}"
    )


print()

print(
    "🚀 Memulai batch upload..."
)

print()


# ============================================================
# COUNTERS
# ============================================================

uploaded_count = 0
failed_count = 0


# ============================================================
# PROCESS EACH JOB
# ============================================================

for index, job_dir in enumerate(
    jobs,
    start=1
):


    print()
    print(
        "=" * 70
    )

    print(
        f"[{index}/{len(jobs)}] "
        f"{job_dir.name}"
    )

    print(
        "=" * 70
    )


    # ========================================================
    # FILES
    # ========================================================

    video_file = (
        job_dir /
        "video.mp4"
    )

    thumbnail_file = (
        job_dir /
        "thumbnail.jpg"
    )

    metadata_file = (
        job_dir /
        "metadata.json"
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    missing = []


    if not video_file.exists():

        missing.append(
            "video.mp4"
        )


    if not metadata_file.exists():

        missing.append(
            "metadata.json"
        )


    if missing:

        print()

        print(
            "❌ Missing:"
        )


        for item in missing:

            print(
                f"   - {item}"
            )


        destination = (
            FAILED_DIR /
            job_dir.name
        )


        safe_failed(
            job_dir,
            destination
        )


        failed_count += 1

        continue


    # ========================================================
    # LOAD METADATA
    # ========================================================

    try:

        metadata = load_json(
            metadata_file
        )


    except Exception as e:

        print()

        print(
            "❌ metadata.json "
            "tidak bisa dibaca."
        )

        print(e)


        destination = (
            FAILED_DIR /
            job_dir.name
        )


        safe_failed(
            job_dir,
            destination
        )


        failed_count += 1

        continue


    # ========================================================
    # METADATA VALUES
    # ========================================================

    title = metadata.get(
        "title",
        job_dir.name
    )


    description = metadata.get(
        "description",
        ""
    )


    tags = metadata.get(
        "tags",
        []
    )
    publish_at = metadata.get(
    "publish_at"
    )   

    # ========================================================
    # DISPLAY
    # ========================================================

    print()

    print(
        f"🎬 Video     : "
        f"{video_file.name}"
    )

    print(
        f"📌 Title     : "
        f"{title}"
    )

    if publish_at:

        print(
            f"📅 Schedule  : "
            f"{publish_at}"
        )

    else:

        print(
            "📅 Schedule  : "
            "IMMEDIATE"
        )

    if thumbnail_file.exists():

        print(
            "🖼️ Thumbnail : YES "
            "(manual)"
        )

    else:

        print(
            "🖼️ Thumbnail : NO"
        )


    # ========================================================
    # REQUEST BODY
    # ========================================================

    # ========================================================
    # PUBLISH SETTINGS
    # ========================================================

    publish_settings = (
        get_publish_settings(
            metadata
        )
    )


    # ========================================================
    # REQUEST BODY
    # ========================================================

    body = {

        "snippet": {

            "title":
                title,

            "description":
                description,

            "tags":
                tags,

            "categoryId":
                CATEGORY_ID,
        },

        "status": {

            **publish_settings,

            "selfDeclaredMadeForKids":
                False,
        }
    }

    # ========================================================
    # MEDIA
    # ========================================================

    media = MediaFileUpload(

        str(video_file),

        chunksize=
            1024 * 1024,

        resumable=True,
    )


    # ========================================================
    # UPLOAD
    # ========================================================

    print()

    print(
        "🚀 Uploading..."
    )


    try:

        request = (
            youtube
            .videos()
            .insert(

                part=
                    "snippet,status",

                body=
                    body,

                media_body=
                    media,
            )
        )


        response = None


        while response is None:

            status, response = (
                request.next_chunk()
            )


            if status:

                progress = int(
                    status.progress()
                    * 100
                )


                print(

                    f"\rUploading... "
                    f"{progress:3d}%",

                    end="",

                    flush=True
                )


        print()


    except Exception as e:

        print()

        print(
            "❌ UPLOAD GAGAL!"
        )

        print()

        print(e)


        destination = (
            FAILED_DIR /
            job_dir.name
        )


        # Lepaskan object
        del media

        del request

        gc.collect()


        safe_failed(
            job_dir,
            destination
        )


        failed_count += 1

        continue


    # ========================================================
    # RELEASE FILE
    # ========================================================

    del media

    del request

    gc.collect()

    time.sleep(2)


    # ========================================================
    # RESPONSE
    # ========================================================

    video_id = response[
        "id"
    ]


    video_url = (
        "https://www.youtube.com/watch?v="
        + video_id
    )


    print()

    print(
        "🎉 UPLOAD BERHASIL!"
    )

    print()

    print(
        f"🆔 Video ID : "
        f"{video_id}"
    )

    print(
        f"🔗 YouTube  : "
        f"{video_url}"
    )


    # ========================================================
    # RESULT
    # ========================================================

    upload_result = {

        "status":
            "uploaded",

        "youtube_id":
            video_id,

        "url":
            video_url,

        "privacy":
            (
                "scheduled"
                if publish_at
                else "public"
            ),

        "publish_at":
            publish_at,
        "thumbnail":
            (
                "manual"
                if thumbnail_file.exists()
                else "missing"
            ),

        "title":
            title,

        "uploaded_at":
            time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
    }


    # ========================================================
    # SAVE RESULT
    # ========================================================

    save_json(

        job_dir /
        "upload_result.json",

        upload_result
    )
    


    # ========================================================
    # ARCHIVE
    # ========================================================

    destination = (
        UPLOADED_DIR /
        job_dir.name
    )


    try:

        safe_archive(
            job_dir,
            destination
        )


    except Exception as e:

        print()

        print(
            "⚠️ Upload sudah sukses,"
            " tapi archive gagal!"
        )

        print(e)

        print()

        print(
            "‼️ JANGAN upload ulang "
            "video ini."
        )

        print()

        print(
            "YouTube:"
        )

        print(
            video_url
        )


        failed_count += 1

        continue


    uploaded_count += 1


    print()

    print(
        "✅ Job selesai."
    )


    # Sedikit jeda antar video
    time.sleep(2)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print()
print("=" * 70)
print("🔥 YOUTUBE PUBLISHER V2 COMPLETE")
print("=" * 70)

print()

print(
    f"Total queue : {len(jobs)}"
)

print(
    f"Uploaded    : {uploaded_count}"
)

print(
    f"Failed      : {failed_count}"
)

print()

print(
    f"Uploaded dir:"
)

print(
    UPLOADED_DIR
)

print()

print(
    f"Failed dir:"
)

print(
    FAILED_DIR
)

print()


if failed_count == 0:

    print(
        "🎉 SEMUA VIDEO BERHASIL!"
    )

else:

    print(
        "⚠️ Ada video yang gagal."
    )

    print(
        "Cek folder publish/failed/"
    )

print()