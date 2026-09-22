import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(url: str) -> str:
    """Fix postgres scheme, reject placeholder URLs, add sslmode for Neon."""
    if not url or not url.strip():
        return "sqlite:///bam_studio.db"

    url = url.strip().strip('"').strip("'")

    # Common mistake: postgres:// → postgresql://
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    # Detect bad placeholders (literal host name "host", example.com, etc.)
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        bad_hosts = {"host", "hostname", "your-host", "localhost.neon.tech", "xxx", "example.com"}
        if hostname in bad_hosts or hostname.endswith(".example"):
            print(f"[config] DATABASE_URL host '{hostname}' looks like a placeholder — using SQLite fallback")
            return "sqlite:///bam_studio.db"
        if parsed.scheme.startswith("postgresql"):
            # Neon requires SSL
            if "sslmode=" not in url:
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}sslmode=require"
    except Exception as e:
        print(f"[config] DATABASE_URL parse error: {e} — using SQLite")
        return "sqlite:///bam_studio.db"

    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production-bam-studio-2026"

    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or "sqlite:///bam_studio.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Serverless-friendly (Vercel): no persistent pool
    _is_pg = SQLALCHEMY_DATABASE_URI.startswith("postgresql")
    SQLALCHEMY_ENGINE_OPTIONS = (
        {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 1,
            "max_overflow": 0,
            "connect_args": {"connect_timeout": 10},
        }
        if _is_pg
        else {}
    )

    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = "static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg", "woff", "woff2", "ttf", "otf"}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600 * 8

    WTF_CSRF_ENABLED = True
    WTF_CSRF_SSL_STRICT = False
    WTF_CSRF_TIME_LIMIT = None

    SESSION_REFRESH_EACH_REQUEST = True
