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
        # self.supported_extensions = {".opus", ".m4a", ".mp3"}
        self.proccessed_songs = 0

    def run(self, paths: list[str]):
        for path_str in paths:
            path = Path(path_str)
            if path.is_dir():
                for file_path in path.iterdir():
                    if file_path.is_file():
                        self.process_song(file_path)

            elif path.is_file():
                self.process_song(path)
            else:
                logger.warning(f"Skipping invalid path or unsupported file: {path}")

        logger.info(f"Processed {self.proccessed_songs} songs.")

    def process_song(self, file_path: Path):
        try:
            audio = TinyTag.get(file_path)
        except Exception as e:
            logger.warning(f"Unsupported file format {file_path}: {e}")
            return

        artist = audio.artist
        album = audio.album
        title = audio.title
        duration = audio.duration
        if title is None or artist is None or album is None or duration is None:
            logger.warning(
                f"Some tags are missing, skipping this song: {title} - {artist} - {album} ({file_path.name})"
            )
            return

        logger.info(
            f"Title: {title}, Artist: {artist}, Album: {album}, Duration: {duration:.2f} seconds"
        )

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
        response = requests.get(f"{self.base_url}/get", params=query_params)
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
