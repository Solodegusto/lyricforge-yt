import re
from typing import Iterable, List
from src.transcriber import LyricSegment


def sanitize_filename(title: str) -> str:
    """Dosya adı için güvenli bir metin üretir."""
    cleaned = re.sub(r'[\\/*?:"<>|]+', "", title).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned[:80] if cleaned else "lyrics"


def _format_srt_timestamp(seconds: float) -> str:
    """Saniyeyi SRT zaman damgasına (HH:MM:SS,mmm) çevirir."""
    total_ms = max(0, int(round(seconds * 1000)))
    hours = total_ms // 3_600_000
    minutes = (total_ms % 3_600_000) // 60_000
    secs = (total_ms % 60_000) // 1000
    millis = total_ms % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _format_lrc_timestamp(seconds: float) -> str:
    """Saniyeyi LRC zaman damgasına ([mm:ss.xx]) çevirir."""
    total_cs = max(0, int(round(seconds * 100)))
    minutes = total_cs // 6000
    secs = (total_cs % 6000) // 100
    centisecs = total_cs % 100
    return f"[{minutes:02d}:{secs:02d}.{centisecs:02d}]"


def to_txt(segments: Iterable[LyricSegment]) -> str:
    """Düz metin (.txt) formatı üretir."""
    lines = [seg.text.strip() for seg in segments if seg.text.strip()]
    return "\n".join(lines)


def to_bilingual_txt(
    orig_segments: List[LyricSegment],
    trans_segments: List[LyricSegment],
) -> str:
    """Orijinal ve çeviri satırlarını alt alta birleştiren düz metin üretir."""
    blocks = []
    for orig, trans in zip(orig_segments, trans_segments):
        blocks.append(f"{orig.text.strip()}\n→ {trans.text.strip()}")
    return "\n\n".join(blocks)


def to_srt(segments: Iterable[LyricSegment]) -> str:
    """Altyazı (.srt) formatı üretir."""
    blocks = []
    idx = 1
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        start_ts = _format_srt_timestamp(seg.start)
        end_ts = _format_srt_timestamp(max(seg.end, seg.start + 0.5))
        blocks.append(f"{idx}\n{start_ts} --> {end_ts}\n{text}")
        idx += 1
    return "\n\n".join(blocks)


def to_bilingual_srt(
    orig_segments: List[LyricSegment],
    trans_segments: List[LyricSegment],
) -> str:
    """İki dilli altyazı (.srt) formatı üretir."""
    blocks = []
    idx = 1
    for orig, trans in zip(orig_segments, trans_segments):
        start_ts = _format_srt_timestamp(orig.start)
        end_ts = _format_srt_timestamp(max(orig.end, orig.start + 0.5))
        blocks.append(f"{idx}\n{start_ts} --> {end_ts}\n{orig.text.strip()}\n{trans.text.strip()}")
        idx += 1
    return "\n\n".join(blocks)


def to_lrc(segments: Iterable[LyricSegment], title: str = "") -> str:
    """Karaoke (.lrc) formatı üretir."""
    header = []
    if title:
        header.append(f"[ti:{title}]")
    header.append("[by:LyricForge YT]")

    lines = []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        ts = _format_lrc_timestamp(seg.start)
        lines.append(f"{ts}{text}")

    return "\n".join(header + lines)
