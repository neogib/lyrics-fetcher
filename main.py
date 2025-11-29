import argparse
import logging
from typing import cast

from rich.logging import RichHandler

from lyrics_downloader import LyricsDownloader


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s -  %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("download_lyrics.log"),
            RichHandler(rich_tracebacks=True),
        ],
    )


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Download lyrics for opus files.")
    _ = parser.add_argument(
        "paths",
        nargs="+",
        help="List of files or directories to process",
    )
    args = parser.parse_args()

    downloader = LyricsDownloader()
    downloader.run(cast(list[str], args.paths))


if __name__ == "__main__":
    main()
