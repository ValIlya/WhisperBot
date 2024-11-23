from io import StringIO

import requests
import webvtt
from yt_dlp import YoutubeDL


class YTClient:
    def __init__(self, proxy: str | None = None, **opts) -> None:
        self.proxy = proxy
        self.ydl_opts = {
            "proxy": self.proxy,
            "cookiesfrombrowser": ("chrome",),
            "skip_download": True,
            "quiet": True,
            "extract_flat": True,  # Extract info only, don't download
            # Transcript
            "writeautomaticsub": True,
            "subtitlesformat": "vtt",
            # Audio
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
            if format != "bestaudio"
            else [],
            **opts,
        }
        self.client = YoutubeDL(self.ydl_opts)

    def get_audio(self, url: str, format: str = "mp3") -> bytearray | None:
        audio_url = self._get_audio_url(url, format=format)
        if not audio_url:
            return None
        return self._request_get(audio_url).content

    def get_transcript(self, url: str) -> str | None:
        subtitles_url = self._get_subtitles_url(url, format="vtt")
        subtitles = self._download_subtitles(subtitles_url)
        srt = self._convert_vtt_to_srt(subtitles)
        return srt

    def _download_subtitles(self, subtitles_url: str) -> str | None:
        return self._request_get(subtitles_url).text

    def _convert_vtt_to_srt(self, vtt_content: str) -> str:
        vtt_file = StringIO(vtt_content)
        vtt_file.name = "subtitles.vtt"  # webvtt requires a filename
        srt_parts = []
        for i, caption in enumerate(webvtt.read_buffer(vtt_file), 1):
            srt_parts.append(
                f"{i}\n{caption.start} --> {caption.end}\n{caption.text}\n"
            )

        return "\n".join(srt_parts)

    def _request_get(self, url: str) -> requests.Response | None:
        proxies = {self.proxy.split("://")[0]: self.proxy} if self.proxy else None
        response = requests.get(url, proxies=proxies)
        return response

    def _get_subtitles_url(self, url: str, format: str = "vtt") -> str | None:
        info = self.client.extract_info(url, download=False)

        lang_captions = info.get("automatic_captions", {})
        language = info.get("language", "en")
        captions = lang_captions.get(language, [])
        for caption in captions:
            if caption["ext"] == format:
                return caption["url"]

        return None

    def _get_audio_url(self, url: str, format: str = "mp3") -> str | None:
        info = self.client.extract_info(url, download=False)
        return info["url"]
