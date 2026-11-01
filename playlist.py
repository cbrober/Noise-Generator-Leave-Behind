"""Build an ordered, validated PCM WAV playlist; no audio output."""

import os
from wav_reader import inspect_wav


def build_playlist(directory, sample_rate):
    names = sorted(name for name in os.listdir(directory)
                   if name.lower().endswith(".wav"))
    if not names:
        raise ValueError("No WAV files found in " + directory)
    tracks = []
    for name in names:
        path = directory.rstrip("/\\") + "/" + name
        try:
            info = inspect_wav(path, sample_rate)
        except (OSError, ValueError) as exc:
            raise ValueError("{}: {}".format(name, exc))
        info["name"] = name
        info["path"] = path
        tracks.append(info)
    return tracks