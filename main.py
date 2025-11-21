from pathlib import Path, PosixPath

import requests
from mutagen.oggopus import OggOpus


def lyrics_for_songs_from_directory(directory_path: str):
    path = Path(directory_path)
    print(path)

    for file_path in path.glob("*.opus"):
        audio: OggOpus = OggOpus(file_path)
        tags = audio.tags
        title = tags.get("title", [""])[0]
        artist = tags.get("artist", [""])[0]
        album = tags.get("album", [""])[0]
        if not all([title, artist, album]):
            print(
                f"Some tags are missing, skipping this song: {title} - {artist} - {album}"
            )
            continue

        duration = audio.info.length
        print(duration)
        print(
            f"Title: {title}, Artist: {artist}, Album: {album}, Duration: {duration:.2f} seconds"
        )

        query_params = {
            "track_name": title,
            "artist_name": artist,
            "album_name": album,
            "duration": int(duration),
        }
        base_url = "https://lrclib.net/api"
        response = requests.get(f"{base_url}/get", params=query_params)
        if response.status_code != 200:
            print(f"Error fetching lyrics: {response.status_code}")
            continue
        data = response.json()
        synced_lyrics = data.get("syncedLyrics", [])
        if not synced_lyrics:
            print("No synced lyrics found.")
            continue
        with open(file_path.with_suffix(".lrc"), "w", encoding="utf-8") as lrc_file:
            metadata = f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n\n"

            lrc_file.write(metadata)

            lrc_file.write(synced_lyrics)


def main():
    full_path = f"{Path.home()}/Music/4now"
    lyrics_for_songs_from_directory(full_path)


if __name__ == "__main__":
    main()
