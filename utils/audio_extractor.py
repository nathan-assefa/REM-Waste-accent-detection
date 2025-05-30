import os
import subprocess
from pydub import AudioSegment
from utils.helpers import remove_file

def extract_audio(video_path: str) -> str:
    """
    Extracts audio from the given video file and saves it as a .wav file
    in mono channel, 16kHz sample rate format suitable for SpeechBrain ECAPA-TDNN.
    
    Args:
        video_path (str): Path to the video file.
    
    Returns:
        str: Path to the extracted and preprocessed audio file (.wav).
    
    Raises:
        FileNotFoundError: If video_path does not exist.
        RuntimeError: If audio extraction or conversion fails.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Prepare output path
    audio_dir = "temp"
    os.makedirs(audio_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(audio_dir, f"{base_name}_audio.wav")

    try:
        # Extract audio with ffmpeg (direct command)
        # This extracts audio and converts it to wav, 16kHz, mono
        command = [
            "ffmpeg",
            "-y",  # overwrite output file if exists
            "-i", video_path,
            "-ac", "1",  # mono audio
            "-ar", "16000",  # 16kHz sampling rate
            "-vn",  # no video
            audio_path
        ]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg error: {result.stderr}")

        # Optional: further normalization or checks with pydub
        audio = AudioSegment.from_wav(audio_path)
        # Normalize audio to -20 dBFS (optional, good for voice models)
        change_in_dBFS = -20.0 - audio.dBFS
        normalized_audio = audio.apply_gain(change_in_dBFS)
        normalized_audio.export(audio_path, format="wav")

        # Once the video gets processed, the file will be deleted to keep the space
        # In the future the files will be stored permanently in bucket.
        remove_file(video_path)

        return audio_path

    except Exception as e:
        raise RuntimeError(f"Audio extraction/conversion failed: {e}")
