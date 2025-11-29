import logging
from pathlib import Path
from typing import final

import requests
from tinytag import TinyTag

logger = logging.getLogger(__name__)


@final
class LyricsDownloader:
    def __init__(self):
        self.base_url = "https://lrclib.net/api"
        self.headers = {
            "User-Agent": "LyricsDownloader v0.0.1 https://github.com/neogib/lyrics-downloader",
        }
        self.supported_extensions = TinyTag.SUPPORTED_FILE_EXTENSIONS
        self.proccessed_songs = 0

    def run(self, paths: list[str]):
        for path_str in paths:
            path = Path(path_str)
            for file_path in path.rglob("*"):
                if file_path.suffix.lower() not in self.supported_extensions:
                    logger.warning(f"Unsupported file format {file_path}, skipping.")
                    continue
                self.process_song(file_path)
        logger.info(f"Processed {self.proccessed_songs} songs.")

    def process_song(self, file_path: Path):
        logger.info(f"Processing file: {file_path}")
        try:
            audio = TinyTag.get(file_path)
        except Exception as e:
            logger.error(f"Error while processing: {file_path}: {e}")
            return

        artist = audio.artist
        album = audio.album
        title = audio.title
        duration = audio.duration

        if title is None or artist is None or album is None or duration is None:
            logger.warning(
                f"Some tags are missing, skipping this song: title: {title}, artist: {artist}, album: {album}, duration: {duration} ({file_path.name})"
            )
            return

        synced_lyrics = self.fetch_lyrics(title, artist, album, duration)
        if synced_lyrics:
            self.save_lyrics(file_path, synced_lyrics, duration, title, artist, album)
            self.proccessed_songs += 1

    def fetch_lyrics(self, title: str, artist: str, album: str, duration: float):
        query_params = {
            "track_name": title,
            "artist_name": artist,
            "album_name": album,
            "duration": int(duration),
        }
        response = requests.get(
            f"{self.base_url}/get", params=query_params, headers=self.headers
        )
        if response.status_code != 200:
            logger.error(f"Error fetching lyrics: {response.status_code}")
            return None

        data = response.json()  # pyright: ignore[reportAny]
        synced_lyrics: str = data.get("syncedLyrics", [])  # pyright: ignore[reportAny]
        if not synced_lyrics:
            logger.info("No synced lyrics found.")
            return None
        return synced_lyrics

    def save_lyrics(
        self,
        file_path: Path,
        synced_lyrics: str,
        duration: float,
        title: str,
        artist: str,
        album: str,
    ):
        with open(file_path.with_suffix(".lrc"), "w", encoding="utf-8") as lrc_file:
            minutes = int(duration // 60)
            secs = int(duration % 60)
            cent = int((duration - int(duration)) * 100)  # hundredths
            time_format = f"{minutes:02d}:{secs:02d}:{cent:02d}"
            metadata = (
                f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n[length:{time_format}]\n\n"
            )

            _ = lrc_file.write(metadata)
            _ = lrc_file.write(synced_lyrics)
