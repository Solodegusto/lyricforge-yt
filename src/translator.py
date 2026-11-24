from typing import List
from deep_translator import GoogleTranslator
from src.transcriber import LyricSegment


class TranslationError(Exception):
    """Çeviri sırasında oluşan hatalar için özel istisna."""


def translate_segments(
    segments: List[LyricSegment],
    target_lang: str,
    source_lang: str = "auto",
) -> List[LyricSegment]:
    """
    Zaman damgalarını koruyarak şarkı sözü segmentlerini hedef dile ('tr', 'en', 'es') çevirir.
    """
    if not segments:
        return []

    raw_lines = [seg.text.strip() for seg in segments]
    separator = "\n|||\n"
    joined_text = separator.join(raw_lines)

    translator = GoogleTranslator(source=source_lang, target=target_lang)

    try:
        translated_blob = translator.translate(joined_text)
        split_lines = [line.strip() for line in translated_blob.split("|||")]

        if len(split_lines) == len(segments):
            return [
                LyricSegment(start=seg.start, end=seg.end, text=t_line or seg.text)
                for seg, t_line in zip(segments, split_lines)
            ]
    except Exception:
        pass

    translated_segments: List[LyricSegment] = []
    try:
        for seg in segments:
            t_text = translator.translate(seg.text.strip())
            translated_segments.append(
                LyricSegment(
                    start=seg.start,
                    end=seg.end,
                    text=(t_text or seg.text).strip(),
                )
            )
        return translated_segments
    except Exception as exc:
        raise TranslationError(f"Translation Error: {exc}") from exc
