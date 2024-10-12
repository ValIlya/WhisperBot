from typing import Generator

import pytest

from whisperbot.speech2text import Speech2Text


@pytest.fixture
def small_model() -> Speech2Text:
    return Speech2Text("small")


@pytest.fixture
def audio() -> Generator:
    with open("samples/jfk.wav", "rb") as f:
        yield f


@pytest.mark.slow
def test_transcribe_auto(small_model, audio):
    res = small_model.transcribe(audio)
    assert res.text != ""
    assert res.language_probs.get("en", 0) > 0.5, res.language_probs.get("en", 0)
