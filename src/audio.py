import os
import tempfile
import uuid
from typing import Tuple
import yt_dlp


class AudioDownloadError(Exception):
    """Ses indirme sırasında oluşan hatalar için özel istisna."""


def download_audio_temp(youtube_url: str) -> Tuple[str, str]:
    """
    Verilen YouTube URL'sinden ses dosyasını geçici bir dizine indirir.

    Returns:
        Tuple[str, str]: (indirilen_dosya_yolu, video_basligi)
    """
    url = youtube_url.strip()
    if not url:
        raise AudioDownloadError("URL_EMPTY")

    temp_dir = tempfile.mkdtemp(prefix="lyricforge_")
    unique_id = uuid.uuid4().hex[:8]
    out_template = os.path.join(temp_dir, f"audio_{unique_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise AudioDownloadError("Video bilgileri alınamadı / Could not fetch video info.")

            title = info.get("title") or "youtube_song"
            downloaded_path = ydl.prepare_filename(info)

            base_path, _ = os.path.splitext(downloaded_path)
            mp3_path = f"{base_path}.mp3"

            if os.path.exists(mp3_path):
                return mp3_path, title
            if os.path.exists(downloaded_path):
                return downloaded_path, title

            for fname in os.listdir(temp_dir):
                full_path = os.path.join(temp_dir, fname)
                if os.path.isfile(full_path):
                    return full_path, title

            raise AudioDownloadError("Ses dosyası diskte bulunamadı / Audio file not found on disk.")

    except yt_dlp.utils.DownloadError as exc:
        cleanup_file(temp_dir)
        raise AudioDownloadError(f"YouTube Download Error: {exc}") from exc
    except AudioDownloadError:
        cleanup_file(temp_dir)
        raise
    except Exception as exc:
        cleanup_file(temp_dir)
        raise AudioDownloadError(f"Unexpected Audio Error: {exc}") from exc


def cleanup_file(path: str) -> None:
    """Dosyayı veya geçici klasörü güvenli şekilde siler."""
    if not path or not os.path.exists(path):
        return
    try:
        if os.path.isfile(path):
            parent = os.path.dirname(path)
            os.remove(path)
            if parent and os.path.isdir(parent) and not os.listdir(parent):
                os.rmdir(parent)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path)
    except OSError:
        pass
