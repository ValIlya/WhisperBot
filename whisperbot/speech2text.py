import io
from pathlib import Path
from typing import Dict, List, Optional

import _pywhispercpp as pwcpp
import numpy as np
import pywhispercpp.constants as constants
from pydantic import BaseModel
from pydub import AudioSegment
from pywhispercpp.model import Model

import whisperbot


class TranscribeResult(BaseModel):
    text: str
    language_probs: Dict[str, float] = {}


class Speech2Text:
    DEFAULT_MODEL = "base"

    def __init__(
        self, model: str | None = None, models_dir: Optional[Path] = None
    ) -> None:
        model = model or self.DEFAULT_MODEL
        self.models_dir = models_dir or Path(whisperbot.__file__).parent / "models"
        self.model = Model(model, models_dir=str(self.models_dir), n_threads=6)

    def _load_audio(self, audio: io.BytesIO) -> np.ndarray:
        sound = AudioSegment.from_file(audio)
        sound = sound.set_frame_rate(constants.WHISPER_SAMPLE_RATE).set_channels(1)
        channel_sounds = sound.split_to_mono()
        samples = [s.get_array_of_samples() for s in channel_sounds]
        arr = np.array(samples).T.astype(np.float32)
        arr /= np.iinfo(samples[0].typecode).max
        return arr

    def transcribe(
        self, audio: io.BytesIO, language: Optional[str] = None
    ) -> TranscribeResult:
        arr = self._load_audio(audio)
        out = []
        segments = self.model.transcribe(arr, language=language)
        for segment in segments:
            out.append(segment.text)
        res = TranscribeResult(text="".join(out))
        if not language or language == "auto":
            res.language_probs = self._get_lang_probs()
        return res

    def _get_lang_probs(self) -> Dict[str, float]:
        lang_probs = np.zeros(pwcpp.whisper_lang_max_id(), dtype=np.float32)
        pwcpp.whisper_lang_auto_detect(
            self.model._ctx,
            0,  # offset_ms
            1,  # n_threads
            lang_probs,
        )
        return {
            pwcpp.whisper_lang_str(lang_id): prob
            for lang_id, prob in enumerate(lang_probs)
        }

    def get_available_languages(self) -> List[str]:
        return ["auto"] + self.model.available_languages()
