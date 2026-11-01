"""Desktop command: py inspect_wav.py path/to/file.wav"""

import sys
import config
from wav_reader import inspect_wav


def main():
    if len(sys.argv) != 2:
        print("Usage: py inspect_wav.py path/to/file.wav")
        return 2
    try:
        config.validate()
        info = inspect_wav(sys.argv[1], config.SAMPLE_RATE)
    except (OSError, ValueError) as exc:
        print("WAV CHECK FAILED:", exc)
        return 1
    print("WAV CHECK PASSED")
    print("Sample rate (Hz):", info["sample_rate"])
    print("Channels:", info["channels"])
    print("Bits per sample:", info["bits"])
    print("Audio starts at byte:", info["data_offset"])
    print("Audio bytes:", info["data_size"])
    print("Duration (seconds): {:.3f}".format(info["duration_seconds"]))
    print("Total file bytes:", info["file_size"])
    print("Inspection only. No sound is played.")
    return 0


if __name__ == "__main__":
    sys.exit(main())