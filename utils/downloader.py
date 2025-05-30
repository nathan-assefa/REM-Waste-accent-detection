import os
import requests
from urllib.parse import urlparse
"""
This file is to download the video from the URL
"""


def download_video(url: str) -> str:
    """
    Downloads a video from a public URL (e.g., Loom or direct MP4).

    Args:
        url (str): The URL of the video.

    Returns:
        str: Path to the downloaded video file.

    Raises:
        ValueError: If the URL is not valid or content is not a video.
        Exception: For any other unexpected issues.
    """
    try:
        # Parse and validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format.")

        # Download content
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, stream=True, timeout=15)
        response.raise_for_status()  # Raise for HTTP errors

        # Check Content-Type
        content_type = response.headers.get("Content-Type", "")
        if "video" not in content_type:
            raise ValueError(f"Unsupported content type: {content_type}")

        # Create temp directory if not exists
        os.makedirs("temp", exist_ok=True)

        # Determine filename
        filename = os.path.basename(parsed_url.path) or "downloaded_video.mp4"
        file_path = os.path.join("temp", filename)

        # Save the video file
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return file_path

    except requests.exceptions.MissingSchema:
        raise ValueError("Malformed URL. Make sure it starts with http:// or https://")

    except requests.exceptions.Timeout:
        raise Exception("The request timed out. Please try again.")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch the video: {e}")

    except Exception as e:
        raise Exception(f"Unexpected error during downloadddd: {e}")
