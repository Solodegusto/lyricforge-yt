from dataclasses import dataclass
from typing import List, Optional
import torch
from faster_whisper import WhisperModel


@dataclass
class LyricSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptionResult:
    language: str
    language_probability: float
    device_used: str
    compute_type_used: str
    segments: List[LyricSegment]


class TranscriptionError(Exception):
    """Transkripsiyon sırasında oluşan hatalar için özel istisna."""


def detect_hardware_config(mode: str = "auto") -> tuple[str, str]:
    """
    Donanım moduna göre ('auto', 'cuda', 'cpu')
    uygun device ve compute_type değerlerini döndürür.
    """
    cuda_available = torch.cuda.is_available()

    if mode == "cuda":
        if not cuda_available:
            raise TranscriptionError("NO_CUDA")
        return "cuda", "float16"

    if mode == "cpu":
        return "cpu", "int8"

    if cuda_available:
        return "cuda", "float16"
    return "cpu", "int8"


def transcribe_audio(
    audio_path: str,
    model_size: str = "small",
    hardware_mode: str = "auto",
    language: Optional[str] = None,
) -> TranscriptionResult:
    """
    Ses dosyasını faster-whisper ile yazıya döker ve dili otomatik algılar.
    """
    device, compute_type = detect_hardware_config(hardware_mode)

    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        segments_iter, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        parsed_segments: List[LyricSegment] = []
        for seg in segments_iter:
            cleaned_text = seg.text.strip()
            if cleaned_text:
                parsed_segments.append(
                    LyricSegment(
                        start=float(seg.start),
                        end=float(seg.end),
                        text=cleaned_text,
                    )
                )

        if not parsed_segments:
            raise TranscriptionError("NO_VOCALS")

        return TranscriptionResult(
            language=info.language,
            language_probability=float(info.language_probability),
            device_used=device,
            compute_type_used=compute_type,
            segments=parsed_segments,
        )

    except TranscriptionError:
        raise
    except Exception as exc:
        raise TranscriptionError(f"Transcription Error: {exc}") from exc
