from pathlib import Path
from typing import List, Optional

from pywhispercpp.model import Model

import whisperbot


class Speech2Text:
    def __init__(
        self, model: str = "base", models_dir: Optional[Path] = None
    ) -> None:
        self.models_dir = models_dir or Path(whisperbot.__file__).parent / "models"
        self.model = Model(
            model, models_dir=str(self.models_dir), n_threads=6
        )

    def transcribe(self, audio: str, language:Optional[str] = None) -> str:
        out = []
        segments = self.model.transcribe(audio, language=language)
        for segment in segments:
            out.append(segment.text)
        return "".join(out)

    def get_available_languages(self) -> List[str]:
        return ['auto'] + self.model.available_languages() 
