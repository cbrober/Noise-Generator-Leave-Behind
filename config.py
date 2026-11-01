"""Edit these settings, then restart the program. No hardware imports here."""

# Bench settings apply only when TEST_MODE is True.
TEST_MODE = True
TEST_START_DELAY_SECONDS = 10
TEST_PLAYBACK_SECONDS = 20

# Normal operating settings: 30-minute delay, then 60-minute playback window.
START_DELAY_SECONDS = 1800
PLAYBACK_SECONDS = 3600
LOOP_AUDIO = True

# Audio storage/decoder choice is deliberately still open.
# This is a candidate PCM sample rate, not a working decoder selection.
SAMPLE_RATE = 16000
AUDIO_DIRECTORY = "TBS_audio"

# GPIO numbers, not physical header pin numbers. Verify against the actual board.
I2S_ID = 0
I2S_BCLK_PIN = 10
I2S_WS_PIN = 11
I2S_DATA_PIN = 9

# None disables LED control until the board's LED pin is confirmed.
# Later this may be a GPIO number or a firmware-supported name such as "LED".
LED_PIN = None
LED_ACTIVE_HIGH = True


def effective_timing():
    """Return (startup delay, playback window), in seconds."""
    if TEST_MODE:
        return TEST_START_DELAY_SECONDS, TEST_PLAYBACK_SECONDS
    return START_DELAY_SECONDS, PLAYBACK_SECONDS


def _nonnegative_integer(name, value):
    if type(value) is not int or value < 0:
        raise ValueError(name + " must be an integer greater than or equal to 0")


def validate():
    """Fail early on invalid settings; callable on Windows or MicroPython."""
    for name, value in (
        ("TEST_MODE", TEST_MODE),
        ("LOOP_AUDIO", LOOP_AUDIO),
        ("LED_ACTIVE_HIGH", LED_ACTIVE_HIGH),
    ):
        if type(value) is not bool:
            raise ValueError(name + " must be True or False")

    for name, value in (
        ("START_DELAY_SECONDS", START_DELAY_SECONDS),
        ("PLAYBACK_SECONDS", PLAYBACK_SECONDS),
        ("TEST_START_DELAY_SECONDS", TEST_START_DELAY_SECONDS),
        ("TEST_PLAYBACK_SECONDS", TEST_PLAYBACK_SECONDS),
        ("I2S_ID", I2S_ID),
        ("I2S_BCLK_PIN", I2S_BCLK_PIN),
        ("I2S_WS_PIN", I2S_WS_PIN),
        ("I2S_DATA_PIN", I2S_DATA_PIN),
    ):
        _nonnegative_integer(name, value)

    if type(SAMPLE_RATE) is not int or SAMPLE_RATE <= 0:
        raise ValueError("SAMPLE_RATE must be a positive integer")
    if not isinstance(AUDIO_DIRECTORY, str) or not AUDIO_DIRECTORY.strip():
        raise ValueError("AUDIO_DIRECTORY must be a nonempty string")

    pins = (I2S_BCLK_PIN, I2S_WS_PIN, I2S_DATA_PIN)
    if len(set(pins)) != 3:
        raise ValueError("I2S pins must be distinct")
    for pin in pins:
        if pin > 29:
            raise ValueError("RP2040 GPIO numbers must be between 0 and 29")

    if LED_PIN is not None:
        if type(LED_PIN) is int:
            if LED_PIN < 0 or LED_PIN > 29 or LED_PIN in pins:
                raise ValueError("LED_PIN must be an unused GPIO between 0 and 29")
        elif not isinstance(LED_PIN, str) or not LED_PIN.strip():
            raise ValueError("LED_PIN must be None, a GPIO number, or a pin name")