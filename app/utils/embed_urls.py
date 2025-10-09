# app/utils/embed_urls.py
import re
from urllib.parse import urlparse, parse_qs

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"}
VIMEO_HOSTS = {"vimeo.com", "www.vimeo.com", "player.vimeo.com"}
DRIVE_HOSTS = {"drive.google.com", "www.drive.google.com"}

def ensure_scheme(url: str) -> str:
    if not url:
        return url
    if url.startswith(("http://", "https://")):
        return url
    return "https://" + url

def to_embed_url(content_type: str, url: str) -> str:
    """
    Convert a normal URL into an embed-friendly URL for iframes.
    Falls back to the original URL if no conversion is needed.
    """
    if not url:
        return url
    try:
        u = urlparse(url)
    except Exception:
        return url

    host = (u.netloc or "").lower()

    # ---------- VIDEO ----------
    if content_type == "video":
        # YouTube
        if host in YOUTUBE_HOSTS:
            # youtu.be/<id>
            if host == "youtu.be":
                video_id = u.path.lstrip("/")
                if video_id:
                    return f"https://www.youtube.com/embed/{video_id}"
                return url
            # youtube.com/watch?v=<id>
            if "watch" in u.path:
                qs = parse_qs(u.query or "")
                vid = (qs.get("v") or [""])[0]
                if vid:
                    return f"https://www.youtube.com/embed/{vid}"
                return url
            # Already embed or other path
            return url

        # Vimeo: vimeo.com/<id> -> player.vimeo.com/video/<id>
        if host in VIMEO_HOSTS:
            m = re.search(r"/(\d+)", u.path or "")
            if m:
                return f"https://player.vimeo.com/video/{m.group(1)}"
            return url

        # Unknown video host: leave as-is
        return url

    # ---------- PDF ----------
    if content_type == "pdf":
        # Google Drive: /file/d/<id>/view -> /preview (embeddable)
        if host in DRIVE_HOSTS and "/file/d/" in u.path:
            try:
                file_id = u.path.split("/file/d/")[1].split("/")[0]
                return f"https://drive.google.com/file/d/{file_id}/preview"
            except Exception:
                return url
        # S3 or any direct .pdf works as-is
        return url

    # ---------- LINK ----------
    # If you also store raw links, we just return as-is.
    return url
