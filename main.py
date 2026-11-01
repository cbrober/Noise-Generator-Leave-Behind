
import config


def main():
    config.validate()
    delay, duration = config.effective_timing()
    print("Audio unit - configuration check only")
    print("Test mode:", config.TEST_MODE)
    print("Startup delay (seconds):", delay)
    print("Playback window (seconds):", duration)
    print("Repeat playlist:", config.LOOP_AUDIO)
    print("Candidate sample rate (Hz):", config.SAMPLE_RATE)
    print("Audio directory:", config.AUDIO_DIRECTORY)
    print("I2S BCLK / WS / DATA GPIO:",
          config.I2S_BCLK_PIN, config.I2S_WS_PIN, config.I2S_DATA_PIN)
    print("Configuration valid. Playback is not implemented yet.")


if __name__ == "__main__":
    main()