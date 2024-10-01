import io
from pathlib import Path
from typing import List, Optional

import numpy as np
import pywhispercpp.constants as constants
from pydub import AudioSegment
from pywhispercpp.model import Model

import whisperbot


class Speech2Text:
    def __init__(self, model: str = "base", models_dir: Optional[Path] = None) -> None:
        self.models_dir = models_dir or Path(whisperbot.__file__).parent / "models"
        self.model = Model(model, models_dir=str(self.models_dir), n_threads=6)

    def transcribe(self, audiofile_path: str, language: Optional[str] = None) -> str:
        out = []
        segments = self.model.transcribe(audiofile_path, language=language)
        for segment in segments:
            out.append(segment.text)
        return "".join(out)

    def _load_audio(self, audio: io.BytesIO) -> np.ndarray:
        sound = AudioSegment.from_file(audio)
        sound = sound.set_frame_rate(constants.WHISPER_SAMPLE_RATE).set_channels(1)
        channel_sounds = sound.split_to_mono()
        samples = [s.get_array_of_samples() for s in channel_sounds]
        arr = np.array(samples).T.astype(np.float32)
        arr /= np.iinfo(samples[0].typecode).max
        return arr

    def transcribe_stream(
        self, audio: io.BytesIO, language: Optional[str] = None
    ) -> str:
        arr = self._load_audio(audio)
        out = []
        segments = self.model.transcribe(arr, language=language)
        for segment in segments:
            out.append(segment.text)
        return "".join(out)

    def get_available_languages(self) -> List[str]:
        return ["auto"] + self.model.available_languages()
