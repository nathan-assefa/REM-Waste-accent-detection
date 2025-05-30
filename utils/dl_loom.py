import argparse
import requests
import sys
import math
import os
from urllib.parse import urlparse
import re
"""
dl_loom.py

A utility module for downloading Loom videos via their public share URLs.

This script allows you to programmatically:
- Extract the session ID from a Loom share URL
- Query Loom's transcoding API to retrieve the video download link
- Download the video file and save it to a local `temp/` directory

Typical usage (from terminal):
    python downloader.py -url https://www.loom.com/share/<session_id>

Typical usage (as a module):
    from downloader import download_loom_video
    file_path = download_loom_video("https://www.loom.com/share/<session_id>")

Raises:
    LoomDownloadError: For any errors encountered during URL parsing, API access, or file downloading.

Author: [Your Name]
"""



class LoomDownloadError(Exception):
    """
    Custom exception raised for any failure during the Loom video download process.
    """
    pass


def extract_session_id(loom_url: str) -> str:
    """
    Extracts the session ID from a Loom share URL.

    Args:
        loom_url (str): The full Loom share URL (e.g., https://www.loom.com/share/<session_id>).

    Returns:
        str: The extracted session ID.

    Raises:
        LoomDownloadError: If the URL is invalid or session ID cannot be extracted.
    """
    match = re.search(r"loom\.com/share/([a-fA-F0-9]+)", loom_url)
    if not match:
        raise LoomDownloadError("Invalid Loom URL format. Could not extract session ID.")
    return match.group(1)


def download_file(url: str, verbose: bool = False) -> str:
    """
    Downloads a file from a given URL and saves it to the `temp/` directory.

    Args:
        url (str): The direct URL to the file.
        verbose (bool): If True, prints progress to the terminal.

    Returns:
        str: The local file path where the video is saved.

    Raises:
        LoomDownloadError: If the file download fails.
    """
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path) or "downloaded_video.mp4"
    os.makedirs("temp", exist_ok=True)
    file_path = os.path.join("temp", filename)

    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_length = response.headers.get("content-length")
            total_length = int(total_length) if total_length else None

            downloaded = 0
            chunk_size = 8192

            if verbose:
                print(f"📥 Downloading and saving as: {file_path}")

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_length and verbose:
                            percent_done = math.floor((downloaded / total_length) * 100)
                            sys.stdout.write(f"\r📥 Downloading ... {percent_done}%")
                            sys.stdout.flush()

            if not total_length and verbose:
                sys.stdout.write("\r📥 Downloading ... 100%\n")

        return file_path

    except requests.RequestException as e:
        raise LoomDownloadError(f"Download failed: {e}") from e


def fetch_video_url(session_id: str, verbose: bool = False) -> str:
    """
    Fetches the direct video URL for a Loom session ID.

    Args:
        session_id (str): The Loom session ID.
        verbose (bool): If True, prints status messages to the terminal.

    Returns:
        str: The direct video download URL.

    Raises:
        LoomDownloadError: If the video URL could not be fetched.
    """
    endpoint = f"https://www.loom.com/api/campaigns/sessions/{session_id}/transcoded-url"

    if verbose:
        print(f"🎬 Fetching video ID: {session_id} ...")

    try:
        response = requests.post(endpoint)
        response.raise_for_status()
        data = response.json()

        video_url = data.get("url")
        if not video_url:
            raise LoomDownloadError("Video URL not found in API response.")

        if verbose:
            print(f"🔗 Video URL: {video_url}")

        return video_url

    except requests.RequestException as e:
        raise LoomDownloadError(f"Failed to fetch video URL: {e}") from e


def download_loom_video(loom_url: str, verbose: bool = False) -> str:
    """
    Orchestrates the process of downloading a Loom public video from its share URL.

    Args:
        loom_url (str): The Loom share URL.
        verbose (bool): If True, prints status and progress to the terminal.

    Returns:
        str: The local file path to the downloaded video.

    Raises:
        LoomDownloadError: If any part of the process fails.

    You can use this public url to test the script
        - url = "https://www.loom.com/share/e41353f2fe1c43eba6c6829693e0f2c5"
    """
    try:
        session_id = extract_session_id(loom_url)
        video_url = fetch_video_url(session_id, verbose=verbose)
        return download_file(video_url, verbose=verbose)
    except LoomDownloadError:
        raise
    except Exception as e:
        raise LoomDownloadError(f"Unexpected error occurred: {e}") from e


def main():
    """
    Entry point when the script is executed from the command line.
    Parses arguments, initiates video download, and prints the output.
    """
    parser = argparse.ArgumentParser(description="Download Loom video by share URL.")
    parser.add_argument(
        "-url", "--url", required=True,
        help="Full Loom share URL (e.g. https://www.loom.com/share/...)"
    )
    args = parser.parse_args()

    try:
        file_path = download_loom_video(args.url, verbose=True)
        print(f"\n✅ Download complete: {file_path}")
    except LoomDownloadError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
