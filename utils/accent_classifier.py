import os
import torch
import torchaudio
import warnings
from speechbrain.inference import EncoderClassifier
from utils.helpers import remove_file
"""
This file has a script to identiy the accent of a speaker
"""


warnings.filterwarnings("ignore")


def detect_accent(audio_path: str) -> dict:
    """
    Detects English accent and returns predicted label, score, and summary.

    Args:
        audio_path (str): Path to the audio file (WAV, 16kHz mono recommended).

    Returns:
        dict: {
            "accent": str,
            "score": float,
            "summary": str
        }

    Raises:
        FileNotFoundError: If the audio file is missing.
        ValueError: If the audio format is invalid.
        RuntimeError: If model inference fails.
        Exception: For unforeseen issues.
    """

    # --- Validate audio file existence ---
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # --- Validate audio format ---
    try:
        waveform, sample_rate = torchaudio.load(audio_path)

        if sample_rate != 16000:
            raise ValueError(f"Expected 16kHz sample rate, got {sample_rate}Hz.")

        if waveform.shape[0] != 1:
            raise ValueError("Audio must be mono channel.")

    except (RuntimeError, OSError, ValueError) as e:
        raise ValueError(f"Invalid audio format: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error validating audio: {e}")

    # --- Load model ---
    try:
        classifier = EncoderClassifier.from_hparams(
            source="Jzuluaga/accent-id-commonaccent_ecapa",
            savedir="pretrained_models/accent-id-commonaccent_ecapa",
            run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
        )
    except (OSError, RuntimeError) as e:
        raise RuntimeError(f"Failed to load the SpeechBrain model: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error loading SpeechBrain model: {e}")

    # --- Run inference ---
    try:
        out_prob, score, index, text_lab = classifier.classify_file(audio_path)
    except (RuntimeError, OSError) as e:
        raise RuntimeError(f"Error during model inference: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error during model inference: {e}")

    # --- Format results ---
    try:
        predicted_accent = text_lab
        confidence_score = round(float(score) * 100, 2)
        
        # Once the audio gets processed, the file will be deleted to keep the space
        remove_file(audio_path)

        return {
            "accent": predicted_accent,
            "score": confidence_score,
            "summary": f"Predicted {predicted_accent} accent with {confidence_score}% confidence."
        }
    except (TypeError, ValueError) as e:
        raise ValueError(f"Error formatting prediction results: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error formatting the results: {e}")
