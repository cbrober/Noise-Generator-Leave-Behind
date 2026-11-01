"""Desktop playlist check. Does not play audio or change files."""

import config
from playlist import build_playlist


def main():
    config.validate()
    try:
        tracks = build_playlist(config.AUDIO_DIRECTORY, config.SAMPLE_RATE)
    except (OSError, ValueError) as exc:
        print("PLAYLIST CHECK FAILED:", exc)
        return False
    print("PLAYLIST CHECK PASSED")
    print("Folder:", config.AUDIO_DIRECTORY)
    total_seconds = 0
    total_bytes = 0
    for index, track in enumerate(tracks):
        print("{}. {} | {:.3f} seconds | {} file bytes".format(
            index + 1, track["name"], track["duration_seconds"], track["file_size"]))
        total_seconds += track["duration_seconds"]
        total_bytes += track["file_size"]
    delay, duration = config.effective_timing()
    print("One playlist pass (seconds): {:.3f}".format(total_seconds))
    print("Total WAV file bytes:", total_bytes)
    print("Startup delay (seconds):", delay)
    print("Playback window (seconds):", duration)
    print("Repeat playlist:", config.LOOP_AUDIO)
    print("Check only. No playback, waiting, or board-storage measurement.")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)