from typing import Iterable, List
from src.transcriber import LyricSegment


def _format_mmss(seconds: float) -> str:
    """Saniyeyi [mm:ss] formatına çevirir."""
    total_sec = max(0, int(round(seconds)))
    minutes = total_sec // 60
    secs = total_sec % 60
    return f"[{minutes:02d}:{secs:02d}]"


def to_plain_text(segments: Iterable[LyricSegment], include_timestamps: bool = False) -> str:
    """Ekranda okumak ve kopyalamak için düz metin üretir."""
    lines = []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        if include_timestamps:
            lines.append(f"{_format_mmss(seg.start)} {text}")
        else:
            lines.append(text)
    return "\n".join(lines)


def to_bilingual_text(
    orig_segments: List[LyricSegment],
    trans_segments: List[LyricSegment],
    include_timestamps: bool = False,
) -> str:
    """Orijinal ve çeviri satırlarını okumak ve kopyalamak için birleştirir."""
    blocks = []
    for orig, trans in zip(orig_segments, trans_segments):
        o_txt = orig.text.strip()
        t_txt = trans.text.strip()
        if not o_txt and not t_txt:
            continue
        prefix = f"{_format_mmss(orig.start)} " if include_timestamps else ""
        blocks.append(f"{prefix}{o_txt}\n{prefix}→ {t_txt}")
    return "\n\n".join(blocks)
