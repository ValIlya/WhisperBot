from pathlib import Path
from typing import Optional

from pywhispercpp.model import Model

import whisperbot


class Speech2Text:
    def __init__(
        self, model: str = "ggml-base.bin", models_dir: Optional[Path] = None
    ) -> None:
        self.models_dir = models_dir or Path(whisperbot.__file__).parent / "models"
        self.model = Model(
            str(self.models_dir / model), models_dir=str(self.models_dir), n_threads=6
        )

    def transcribe(self, audio: str) -> str:
        out = []
        segments = self.model.transcribe(audio)
        for segment in segments:
            out.append(segment.text)
        return "".join(out)
