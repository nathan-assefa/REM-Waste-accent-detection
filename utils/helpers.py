import os
"""
This file comprises a utility functions 
"""


def remove_file(path: str) -> None:
    """
    Safely deletes the file at the specified path.

    Args:
        path (str): Path to the file to be deleted.
    """
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass  # Silently ignore errors
