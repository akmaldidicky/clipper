# ============================================================
# 🔥 CLIPPER MACHINE — FINAL RUNNER V3
#
# Fungsi:
#   1. Menjalankan caption_generator.py
#   2. Menjalankan add_cover.py
#   3. Membuat metadata YouTube
#   4. Membuat hashtag berdasarkan konteks video
#   5. Menyiapkan YouTube publish queue
#   6. Upload batch ke YouTube
#
# FINAL/ SUDAH DIHAPUS
#
# Cara menjalankan:
#   py final.py
# ============================================================

import shutil
import subprocess
import sys
import json
import time
import gc
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


CAPTION_SCRIPT = (
    BASE_DIR /
    "caption_generator.py"
)


THUMBNAIL_SCRIPT = (
    BASE_DIR /
    "add_cover.py"
)


# ------------------------------------------------------------
# SOURCE
# ------------------------------------------------------------

SUBTITLED_DIR = (
    BASE_DIR /
    "subtitled"
)


CAPTIONS_DIR = (
    BASE_DIR /
    "captions"
)


THUMBNAILS_DIR = (
    BASE_DIR /
    "thumbnails"
)


TITLE_DIR = (
    BASE_DIR /
    "temp_thumbnail_text"
)


# ------------------------------------------------------------
# YOUTUBE
# ------------------------------------------------------------

YOUTUBE_PUBLISHER = (
    BASE_DIR /
    "youtube" /
    "youtube_publisher.py"
)


QUEUE_DIR = (
    BASE_DIR /
    "publish" /
    "queue"
)


# ============================================================
# YOUTUBE SETTINGS
# ============================================================

DEFAULT_TAGS = [
    "paripurna",
    "rapat paripurna",
    "menteri",
    "demo",
    "presiden",
    "demo",
    "27Agustus",
    "RUUPERAMPASANASET",
    # "pati",
]
# ============================================================
# YOUTUBE SCHEDULER
# ============================================================

# True  = video dijadwalkan
# False = video langsung public
SCHEDULE_ENABLED = True


# Jadwal video pertama
#
# Format:
# YYYY-MM-DD HH:MM
#
# Contoh:
# 2026-08-27 18:00
SCHEDULE_START = "2026-08-28 05:00"


# Jarak antar video dalam menit
#
# 120 = setiap 2 jam
# 60  = setiap 1 jam
# 180 = setiap 3 jam
SCHEDULE_INTERVAL_MINUTES = 7


# Zona waktu Indonesia Barat
SCHEDULE_TIMEZONE = "Asia/Jakarta"

# ============================================================
# HASHTAG SETTINGS
# ============================================================

# Hashtag berdasarkan konteks.
#
# Sistem membaca:
#   TITLE + CAPTION
#
# lalu mencari keyword yang relevan.
#
# Tidak menggunakan AI/API tambahan.
# ============================================================

HASHTAG_RULES = {

    # --------------------------------------------------------
    # BUKU / MEMBACA
    # --------------------------------------------------------

    "#Buku": [
        "buku",
        "books",
        "book",
    ],

    "#Membaca": [
        "membaca",
        "baca",
        "bacaan",
        "reading",
    ],

    "#RekomendasiBuku": [
        "rekomendasi buku",
        "rekomendasi",
        "buku favorit",
        "favorite book",
        "buku yang saya suka",
    ],

    "#AtomicHabits": [
        "atomic habits",
    ],

    "#HomoDeus": [
        "homo deus",
    ],


    # --------------------------------------------------------
    # SELF DEVELOPMENT
    # --------------------------------------------------------

    "#SelfImprovement": [
        "self improvement",
        "pengembangan diri",
        "mengembangkan diri",
        "perbaiki diri",
        "memperbaiki diri",
    ],

    "#Mindset": [
        "mindset",
        "pola pikir",
        "cara berpikir",
        "berpikir",
    ],

    "#Motivasi": [
        "motivasi",
        "semangat",
        "termotivasi",
        "inspirasi",
        "inspiratif",
    ],


    # --------------------------------------------------------
    # CRITICAL THINKING
    # --------------------------------------------------------

    "#BerpikirKritis": [
        "berpikir kritis",
        "berpikir secara kritis",
        "pemikiran kritis",
        "cara berpikir kritis",
    ],

    "#CriticalThinking": [
        "critical thinking",
    ],

    "#Logika": [
        "logika",
        "logical",
        "penalaran",
        "bernalar",
    ],


    # --------------------------------------------------------
    # BISNIS
    # --------------------------------------------------------

    "#Bisnis": [
        "bisnis",
        "usaha",
        "berbisnis",
        "business",
    ],

    "#Entrepreneur": [
        "entrepreneur",
        "entrepreneurship",
        "pengusaha",
        "wirausaha",
        "kewirausahaan",
    ],

    "#BusinessMindset": [
        "business mindset",
        "mindset bisnis",
        "pola pikir bisnis",
    ],
        # --------------------------------------------------------
    # GAME / GAMING
    # --------------------------------------------------------

    "#Gaming": [
        "game",
        "gaming",
        "gamer",
        "video game",
        "videogame",
        "permainan",
        "main game",
        "bermain game",
    ],

    "#Gamer": [
        "gamer",
        "gaming",
        "player",
        "pemain game",
    ],

    "#GameIndonesia": [
        "game indonesia",
        "gamer indonesia",
        "gaming indonesia",
    ],

    "#MobileGaming": [
        "mobile game",
        "mobile gaming",
        "game mobile",
        "hp gaming",
        "android game",
    ],

    "#PCGaming": [
        "pc gaming",
        "game pc",
        "gaming pc",
        "komputer gaming",
    ],


    # --------------------------------------------------------
    # HUMOR / COMEDY
    # --------------------------------------------------------

    "#Humor": [
        "humor",
        "lucu",
        "kelucuan",
        "ngakak",
        "kocak",
        "lawak",
        "becanda",
        "bercanda",
    ],

    "#Komedi": [
        "komedi",
        "comic",
        "comedy",
        "comedian",
        "pelawak",
    ],

    "#Lucu": [
        "lucu",
        "ngakak",
        "kocak",
        "gokil",
        "absurd",
    ],

    "#Meme": [
        "meme",
        "memes",
        "meme lucu",
    ],


    # --------------------------------------------------------
    # SEPAK BOLA
    # --------------------------------------------------------

    "#SepakBola": [
        "sepak bola",
        "sepakbola",
        "football",
        "soccer",
        "bola",
        "pemain bola",
    ],

    "#Football": [
        "football",
        "soccer",
        "sepak bola",
        "sepakbola",
    ],

    "#Futbol": [
        "futbol",
    ],

    "#LigaIndonesia": [
        "liga indonesia",
        "liga 1",
        "liga 2",
        "persib",
        "persija",
        "persebaya",
        "arema",
        "psm",
        "bali united",
    ],

    "#TimnasIndonesia": [
        "timnas",
        "tim nasional",
        "timnas indonesia",
        "indonesia national team",
    ],

    "#PremierLeague": [
        "premier league",
        "liga inggris",
        "manchester united",
        "manchester city",
        "liverpool",
        "arsenal",
        "chelsea",
        "tottenham",
    ],

    "#ChampionsLeague": [
        "champions league",
        "liga champions",
        "ucl",
        "uefa champions league",
    ],


    # --------------------------------------------------------
    # OLAHRAGA
    # --------------------------------------------------------

    "#Olahraga": [
        "olahraga",
        "sport",
        "sports",
        "atlet",
        "atletik",
        "pertandingan",
    ],

    "#Basket": [
        "basket",
        "basketball",
        "nba",
        "pemain basket",
    ],

    "#Badminton": [
        "badminton",
        "bulu tangkis",
        "bulutangkis",
    ],

    "#Tennis": [
        "tennis",
        "tenis",
        "tennis player",
    ],

    "#F1": [
        "formula 1",
        "formula one",
        "f1",
        "grand prix",
        "grandprix",
    ],

    "#MotoGP": [
        "motogp",
        "moto gp",
        "motor gp",
    ],

    "#Boxing": [
        "boxing",
        "tinju",
        "petinju",
        "boxer",
    ],

    "#MMA": [
        "mma",
        "ufc",
        "mixed martial arts",
    ],

    "#Fitness": [
        "fitness",
        "gym",
        "workout",
        "latihan",
        "olahraga gym",
    ],


    # --------------------------------------------------------
    # LIFESTYLE
    # --------------------------------------------------------

    "#Lifestyle": [
        "lifestyle",
        "gaya hidup",
        "kehidupan sehari-hari",
        "keseharian",
    ],

    "#DailyLife": [
        "daily life",
        "sehari-hari",
        "keseharian",
        "rutinitas harian",
    ],

    "#HealthyLifestyle": [
        "healthy lifestyle",
        "gaya hidup sehat",
        "hidup sehat",
        "kesehatan",
    ],

    "#Minimalism": [
        "minimalis",
        "minimalism",
        "hidup minimalis",
    ],

    "#Travel": [
        "travel",
        "traveling",
        "travelling",
        "perjalanan",
        "liburan",
        "wisata",
        "jalan-jalan",
    ],

    "#Food": [
        "makanan",
        "kuliner",
        "food",
        "masakan",
        "memasak",
        "resep",
        "kulineran",
    ],

    "#Technology": [
        "teknologi",
        "technology",
        "tech",
        "gadget",
        "smartphone",
        "ai",
        "artificial intelligence",
    ],

    # --------------------------------------------------------
    # KEUANGAN
    # --------------------------------------------------------

    "#Keuangan": [
        "keuangan",
        "uang",
        "finansial",
        "financial",
        "financial literacy",
    ],

    "#Investasi": [
        "investasi",
        "invest",
        "investing",
        "saham",
        "reksadana",
        "crypto",
        "kripto",
    ],

    "#FinancialLiteracy": [
        "literasi keuangan",
        "financial literacy",
        "literasi finansial",
    ],


    # --------------------------------------------------------
    # PSYCHOLOGY
    # --------------------------------------------------------

    "#Psikologi": [
        "psikologi",
        "psychology",
        "psikologis",
    ],

    "#Psychology": [
        "psychology",
        "psychological",
    ],


    # --------------------------------------------------------
    # RELATIONSHIP
    # --------------------------------------------------------

    "#Relationship": [
        "relationship",
        "hubungan",
        "pasangan",
        "pernikahan",
        "pacaran",
        "percintaan",
    ],

    "#Love": [
        "cinta",
        "love",
        "mencintai",
        "dicintai",
    ],


    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    "#Pendidikan": [
        "pendidikan",
        "belajar",
        "pelajaran",
        "edukasi",
        "education",
    ],

    "#Belajar": [
        "belajar",
        "mempelajari",
        "pembelajaran",
    ],


    # --------------------------------------------------------
    # PRODUCTIVITY
    # --------------------------------------------------------

    "#Produktivitas": [
        "produktif",
        "produktivitas",
        "productivity",
        "time management",
        "manajemen waktu",
        "mengatur waktu",
    ],


    # --------------------------------------------------------
    # CAREER
    # --------------------------------------------------------

    "#Karier": [
        "karier",
        "career",
        "pekerjaan",
        "bekerja",
        "profesi",
        "kantor",
    ],
}


# ============================================================
# TERMINAL COLORS
# ============================================================

RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"


# ============================================================
# PRINT HELPERS
# ============================================================

def print_header(text):

    print()
    print("=" * 70)

    print(
        f"{BOLD}{CYAN}"
        f"{text}"
        f"{RESET}"
    )

    print("=" * 70)


def print_success(text):

    print(
        f"{GREEN}✅ "
        f"{text}"
        f"{RESET}"
    )


def print_error(text):

    print(
        f"{RED}❌ "
        f"{text}"
        f"{RESET}"
    )


def print_warning(text):

    print(
        f"{YELLOW}⚠ "
        f"{text}"
        f"{RESET}"
    )


def print_info(text):

    print(
        f"{CYAN}ℹ "
        f"{text}"
        f"{RESET}"
    )


# ============================================================
# CHECK FILE
# ============================================================

def check_file(file_path):

    if not file_path.exists():

        print_error(
            f"File tidak ditemukan: "
            f"{file_path}"
        )

        return False


    print_success(
        f"{file_path.name} ditemukan"
    )

    return True


# ============================================================
# RUN PYTHON SCRIPT
# ============================================================

def run_script(script_path):

    print()
    print("-" * 70)

    print(
        f"▶ Menjalankan: "
        f"{script_path.name}"
    )

    print("-" * 70)
    print()


    result = subprocess.run(

        [
            sys.executable,
            str(script_path),
        ],

        cwd=BASE_DIR,
    )


    if result.returncode != 0:

        print_error(
            f"{script_path.name} gagal."
        )

        return False


    print()

    print_success(
        f"{script_path.name} selesai."
    )

    return True


# ============================================================
# READ TEXT
# ============================================================

def read_text(path):

    return path.read_text(
        encoding="utf-8"
    ).strip()


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    path,
    data
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


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

# ============================================================
# GENERATE PUBLISH SCHEDULE
# ============================================================

def generate_publish_time(index):

    """
    Membuat waktu publish berdasarkan urutan video.

    index:
        0 = video pertama
        1 = video kedua
        2 = video ketiga
        dst.
    """

    timezone = ZoneInfo(
        SCHEDULE_TIMEZONE
    )


    start_time = datetime.strptime(
        SCHEDULE_START,
        "%Y-%m-%d %H:%M"
    )


    start_time = start_time.replace(
        tzinfo=timezone
    )


    publish_time = (
        start_time
        +
        timedelta(
            minutes=
                SCHEDULE_INTERVAL_MINUTES
                * index
        )
    )


    # RFC3339 / ISO format
    return publish_time.isoformat()
# ============================================================
# GENERATE HASHTAGS
# ============================================================

def generate_hashtags(
    title,
    caption
):

    """
    Membuat hashtag berdasarkan konteks
    title + caption.

    Tidak menggunakan API / AI tambahan.

    Return:
        list[str]
    """


    # --------------------------------------------------------
    # GABUNGKAN TITLE + CAPTION
    # --------------------------------------------------------

    context = (

        f"{title} "

        f"{caption}"
    ).lower()


    # --------------------------------------------------------
    # HASHTAG RESULT
    # --------------------------------------------------------

    hashtags = []


    # --------------------------------------------------------
    # CHECK RULES
    # --------------------------------------------------------

    for hashtag, keywords in (
        HASHTAG_RULES.items()
    ):

        for keyword in keywords:

            if keyword.lower() in context:

                hashtags.append(
                    hashtag
                )

                break


    # --------------------------------------------------------
    # LIMIT
    # --------------------------------------------------------

    # Jangan terlalu banyak hashtag.
    #
    # Maksimal:
    #   6 hashtag konteks
    #
    # + #shorts
    # --------------------------------------------------------

    hashtags = hashtags[:6]


    # --------------------------------------------------------
    # ALWAYS SHORTS
    # --------------------------------------------------------

    if "#shorts" not in (
        h.lower()
        for h in hashtags
    ):

        hashtags.append(
            "#shorts"
        )


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if len(hashtags) == 1:

        hashtags.insert(
            0,
            "#Podcast"
        )


    return hashtags


# ============================================================
# PREPARE YOUTUBE QUEUE
# ============================================================

def prepare_youtube_queue():

    print_header(
        "🚀 STEP 4 — PREPARE YOUTUBE QUEUE"
    )


    # --------------------------------------------------------
    # CHECK SOURCE
    # --------------------------------------------------------

    required_dirs = [

        SUBTITLED_DIR,

        CAPTIONS_DIR,

        THUMBNAILS_DIR,

        TITLE_DIR,

    ]


    for directory in required_dirs:

        if not directory.exists():

            print_error(
                f"Folder tidak ditemukan: "
                f"{directory}"
            )

            return False


    # --------------------------------------------------------
    # CREATE QUEUE
    # --------------------------------------------------------

    QUEUE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # FIND FINAL VIDEOS
    # --------------------------------------------------------

    videos = sorted(

        SUBTITLED_DIR.glob(
            "final_*.mp4"
        )

    )


    print()

    print(
        f"🎬 Final videos : "
        f"{len(videos)}"
    )

    print(
        f"📦 Queue        : "
        f"{QUEUE_DIR}"
    )


    if not videos:

        print_warning(
            "Tidak ada final video."
        )

        return False


    # --------------------------------------------------------
    # COUNTERS
    # --------------------------------------------------------

    prepared = 0
    skipped = 0


    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    for video in videos:

        # ----------------------------------------------------
        # NUMBER
        # ----------------------------------------------------

        number = (

            video.stem
            .replace(
                "final_",
                ""
            )

        )


        job_name = (

            f"short_{number}"

        )


        print()
        print("-" * 70)

        print(
            f"🎬 {video.name}"
        )

        print(
            f"📦 → {job_name}"
        )


        # ----------------------------------------------------
        # SOURCE FILES
        # ----------------------------------------------------

        caption_file = (

            CAPTIONS_DIR /

            f"clip_{number}.txt"

        )


        thumbnail_file = (

            THUMBNAILS_DIR /

            f"thumbnail_{number}.jpg"

        )


        title_file = (

            TITLE_DIR /

            f"title_{number}.txt"

        )


        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        missing = []


        if not video.exists():

            missing.append(
                "video"
            )


        if not caption_file.exists():

            missing.append(
                "caption"
            )


        if not thumbnail_file.exists():

            missing.append(
                "thumbnail"
            )


        if not title_file.exists():

            missing.append(
                "title"
            )


        if missing:

            print_warning(
                "SKIP — file kurang:"
            )


            for item in missing:

                print(
                    f"   - {item}"
                )


            skipped += 1

            continue


        # ----------------------------------------------------
        # READ
        # ----------------------------------------------------

        try:

            # =================================================
            # TITLE — FORCE SINGLE LINE
            # =================================================

            title = " ".join(

                read_text(
                    title_file
                ).split()

            )


            # =================================================
            # CAPTION
            # =================================================

            caption = read_text(
                caption_file
            )


        except Exception as error:

            print_error(
                f"Gagal membaca metadata: "
                f"{error}"
            )

            skipped += 1

            continue


        # ----------------------------------------------------
        # FALLBACK TITLE
        # ----------------------------------------------------

        if not title:

            title = (

                f"Shorts #{number}"

            )


        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        description = caption


        # ----------------------------------------------------
        # GENERATE HASHTAGS
        # ----------------------------------------------------

        hashtags = generate_hashtags(

            title,

            caption

        )


        # ----------------------------------------------------
        # ADD HASHTAGS TO DESCRIPTION
        # ----------------------------------------------------

        hashtag_text = " ".join(
            hashtags
        )


        description = (

            description.rstrip()

            + "\n\n"

            + hashtag_text

        )


        # ----------------------------------------------------
        # QUEUE DIRECTORY
        # ----------------------------------------------------

        job_dir = (

            QUEUE_DIR /

            job_name

        )


        job_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        # ----------------------------------------------------
        # DESTINATION
        # ----------------------------------------------------

        destination_video = (

            job_dir /

            "video.mp4"

        )


        destination_thumbnail = (

            job_dir /

            "thumbnail.jpg"

        )


        metadata_file = (

            job_dir /

            "metadata.json"

        )


        # ----------------------------------------------------
        # COPY VIDEO
        # ----------------------------------------------------

        shutil.copy2(

            video,

            destination_video

        )


        # ----------------------------------------------------
        # COPY THUMBNAIL
        # ----------------------------------------------------

        shutil.copy2(

            thumbnail_file,

            destination_thumbnail

        )
        # --------------------------------------------------------
# PUBLISH SCHEDULE
# --------------------------------------------------------

        publish_at = None
        
        
        if SCHEDULE_ENABLED:
        
            publish_at = generate_publish_time(
                prepared
            )



        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

            metadata = {
            
                "title":
                    title,
            
                "description":
                    description,
            
                "hashtags":
                    hashtags,
            
                "tags":
                    DEFAULT_TAGS,
            
                "publish_at":
                    publish_at,
            
                "source_video":
                    str(video),
            
                "source_caption":
                    str(caption_file),
            
                "source_thumbnail":
                    str(thumbnail_file),
            
                "source_title":
                    str(title_file),
            }


        save_json(

            metadata_file,

            metadata

        )


        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        print()

        print(
            f"📌 Title     : "
            f"{title}"
        )
        if publish_at:
        
            print(
                f"📅 Publish   : "
                f"{publish_at}"
            )

        else:
        
            print(
                "📅 Publish   : "
                "IMMEDIATE"
            )
        print(
            "📝 Caption   : OK"
        )

        print(
            "🖼️ Thumbnail : OK"
        )

        print(
            "🏷️ Hashtags  : "
            + " ".join(hashtags)
        )

        print(
            "📄 Metadata  : OK"
        )

        print_success(
            "QUEUE READY"
        )


        prepared += 1


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()

    print(
        f"Prepared : "
        f"{prepared}"
    )

    print(
        f"Skipped  : "
        f"{skipped}"
    )


    if prepared == 0:

        print_error(
            "Tidak ada video yang masuk queue."
        )

        return False


    print()

    print_success(
        f"{prepared} video siap upload."
    )

    return True


# ============================================================
# YOUTUBE UPLOAD
# ============================================================

def run_youtube_publisher():

    print_header(
        "🚀 STEP 5 — YOUTUBE PUBLISHER"
    )


    if not check_file(
        YOUTUBE_PUBLISHER
    ):

        return False


    print()

    print(
        "🚀 Menjalankan YouTube Publisher..."
    )

    print()


    result = subprocess.run(

        [
            sys.executable,

            str(
                YOUTUBE_PUBLISHER
            ),

        ],

        cwd=BASE_DIR,

    )


    if result.returncode != 0:

        print_error(
            "YouTube Publisher gagal."
        )

        return False


    print()

    print_success(
        "YouTube Publisher selesai."
    )


    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print_header(
        "🔥 CLIPPER MACHINE — FINAL RUNNER V3"
    )


    print()

    print(
        "Pipeline:"
    )

    print(
        "  1. Caption Generator"
    )

    print(
        "  2. Thumbnail Generator"
    )

    print(
        "  3. Context Hashtag Generator"
    )

    print(
        "  4. Prepare YouTube Queue"
    )

    print(
        "  5. YouTube Publisher"
    )

    print()


    # ========================================================
    # STEP 1 — CHECK
    # ========================================================

    print_header(
        "🔍 STEP 1 — CHECK FILES"
    )


    if not check_file(
        CAPTION_SCRIPT
    ):

        return 1


    if not check_file(
        THUMBNAIL_SCRIPT
    ):

        return 1


    if not check_file(
        YOUTUBE_PUBLISHER
    ):

        return 1


    # ========================================================
    # STEP 2 — CAPTION
    # ========================================================

    print_header(
        "📝 STEP 2 — CAPTION GENERATOR"
    )


    if not run_script(
        CAPTION_SCRIPT
    ):

        print_error(
            "Pipeline dihentikan."
        )

        return 1


    # ========================================================
    # STEP 3 — THUMBNAIL
    # ========================================================

    print_header(
        "🖼️ STEP 3 — THUMBNAIL GENERATOR"
    )


    if not run_script(
        THUMBNAIL_SCRIPT
    ):

        print_error(
            "Pipeline dihentikan."
        )

        return 1


    # ========================================================
    # STEP 4 — PREPARE QUEUE
    # ========================================================

    if not prepare_youtube_queue():

        print_error(
            "Prepare queue gagal."
        )

        return 1


    # ========================================================
    # STEP 5 — YOUTUBE
    # ========================================================

    if not run_youtube_publisher():

        print_error(
            "Upload YouTube gagal."
        )

        return 1


    # ========================================================
    # FINAL
    # ========================================================

    print_header(
        "🎉 CLIPPER MACHINE SELESAI"
    )


    print()

    print_success(
        "Video berhasil diproses."
    )

    print()

    print(
        "📦 Queue:"
    )

    print(
        f"   {QUEUE_DIR}"
    )

    print()

    print(
        "🎬 YouTube upload selesai."
    )

    print()

    print_info(
        "Hashtag otomatis dibuat "
        "berdasarkan title + caption."
    )

    print()

    return 0


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )