# this is not yet complete, my hardware gets here next week. I will finish it then.


# RP2040 

This project is going to be a bit more involved than the previous because it does not have the more advanced computing ability that exists natively in the pi desktop. Here we will actually need to build the software that runs the whole operation. 

(Context) I will be building the software in advanced using VSCode, while I wait to get all of the ordered physical components.  All of the notes will have specific caveats for VSCode added, but if that's not what you're using you can just skip those. 


# STEP 1 

Here we are going to create the initial structure for files. If you haven't already installed python and added the plugins for python to your VSCode, do that now (or you will not be able to follow along or fix and debug that code as you move along). 

## Create the project folder

Create a folder named `TBS_audio_unit` (or whatever you want to name it, but remember to change that our in all your directories).

Open VS Code, choose **File > Open Folder**, and select the folder you just made.
In VS Code's Explorer panel, create a subfolder named `TBS_audio` and two .py files named main and config.

 By the end, your software project should look like this:

```text
TBS_audio_unit/
    main.py
    config.py
    TBS_audio/
```

## Check desktop Python

Open **Terminal > New Terminal** in VS Code. Use PowerShell.

```powershell
python --version
```

Expected: a Python 3 version number. If that command fails, try:

```powershell
py --version
```

If neither works, you have either not installed Python for Windows or there is a config problem with your download. Try uninstalling and reinstalling or just download it for the first time. 

## 3. Create config.py

In VS Code's Explorer panel, navigate to the `config.py` file and paste the below into it. **YOU ARE PASTING THIS INTO THE FILE NOT INTO THE TERMINAL**
Now save with **Ctrl+S**. 

```python
"""You can edit these settings to your desired parameters, then restart the program to ensure it is running appropriately."""

TEST_MODE = True
TEST_START_DELAY_SECONDS = 5
TEST_PLAYBACK_SECONDS = 20

# This is where you are going to make your edits for the operational delay I will be setting mine to 30 minutes with a run time of 60 minutes. During testing you should play around with this so you are not waiting 30-90 minutes each test. 

START_DELAY_SECONDS = 1800
PLAYBACK_SECONDS = 3600
LOOP_AUDIO = True

# Audio storage/decoder choice is deliberately still open.
# This is a temporary sample rate that can and probably will be changed later depending on how the audio sounds.

SAMPLE_RATE = 22050
AUDIO_DIRECTORY = "TBS_audio"

# This is the map for the GPIO numbers, not physical header pin numbers. Ensure you are checking your board to match up with these GPIO selections.

I2S_ID = 0
I2S_BCLK_PIN = 10
I2S_WS_PIN = 11
I2S_DATA_PIN = 9

# None disables LED control until the board's LED pin is confirmed. While working this we may use the LED during testing but will disable for operation.
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

```

## main.py

Navigate to the `main.py` file you made in the TBS_audio_unit folder you made.
**Paste the entire block below and save.**

```python

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
```

## 5. Run the config check

In the terminal, with `TBS_audio_unit` as the current folder, run:

```powershell
python main.py
```

or 

```powershell
py main.py
```

You should get this back:

```text
Audio unit - configuration check only
Test mode: True
Startup delay (seconds): 5
Playback window (seconds): 20
Repeat playlist: True
Candidate sample rate (Hz): 22050
Audio directory: TBS_audio
I2S BCLK / WS / DATA GPIO: 10 11 9
Configuration valid. Playback is not implemented yet.
```

The printed times describe the future controller; this version should not wait or produce sound.

## Test changes and ensure they work

In `config.py` go to the top lines and change the TEST_START_DELAY_SECONDS time and save **Ctl+S**:

```python
TEST_START_DELAY_SECONDS = 10
```

In the terminal/pwrshell press the up arrow and rerun the command. You should get a similar output, except now the startup delay should say 10 seconds. 

We have built in this test to ensure that the simple functions in the code work properly, later we will hash these lines out/set test mode to false so the code will default to the operational settings. 



# STEP 2 

Here we are going to built the controller file to go through the steps of delay then play then end sequence. **DO NOT CHANGE ANYTHING WITH THE PREVIOUS FILES IN THIS STEP** 

##  Create controller.py and simulate.py

Under the same main folder `TBS_audio_unit`. Create these two files, and you folder should look like this (potentially also having the pycache there from the previous step)

controller.py owns timing and state. It asks a player to start, polls whether
playback is still active, and stops the player when the window expires. If the
player raises an exception, it records ERROR and attempts to stop output.

simulate.py supplies elapsed time and a fake player. The fake player stays active
until stopped. The future real player will handle sequential files and LOOP_AUDIO. Both WAV and compressed audio can use the same controller interface.

The controller checks its deadline frequently instead of sleeping for the full
playback duration. The desktop runner check will roughly every 20 milliseconds (specified later).

```text
TBS_audio_unit/
    main.py
    config.py
    controller.py
    simulate.py
    TBS_audio/
```

Paste the below into the controller.py file **NOT INTO THE TERMINAL** .

```python
class Controller:
    def __init__(self, player, delay_seconds, playback_seconds, loop_audio=True):
        for value in (delay_seconds, playback_seconds):
            if type(value) is not int or value < 0:
                raise ValueError("Durations must be nonnegative integer seconds")
        self.player = player
        self.delay_ms = delay_seconds * 1000
        self.duration_ms = playback_seconds * 1000
        self.loop_audio = loop_audio
        self.state = "WAITING"
        self.error = None
        self.play_started_ms = None

    def update(self, elapsed_ms):
        """Call frequently with monotonically increasing time since startup.

        Player contract: start(loop_audio), poll(), stop(). poll returns True
        while active and False when the playlist ends. These calls must return
        promptly so the controller can enforce the playback deadline.
        """
        if self.state in ("FINISHED", "ERROR"):
            return
        try:
            if self.state == "WAITING":
                if elapsed_ms < self.delay_ms:
                    return
                if self.duration_ms == 0:
                    self.state = "FINISHED"
                    return
                self.player.start(self.loop_audio)
                self.play_started_ms = elapsed_ms
                self.state = "PLAYING"
            if self.state == "PLAYING":
                if elapsed_ms - self.play_started_ms >= self.duration_ms:
                    self.player.stop()
                    self.state = "FINISHED"
                elif not self.player.poll():
                    self.player.stop()
                    self.state = "FINISHED"
        except Exception as exc:
            self.error = str(exc)
            self.state = "ERROR"
            try:
                self.player.stop()
            except Exception:
                pass  # Preserve the original failure for reporting.

    def cancel(self):
        """Stop output when the runner is interrupted."""
        if self.state not in ("FINISHED", "ERROR"):
            try:
                self.player.stop()
                self.state = "FINISHED"
            except Exception as exc:
                self.error = str(exc)
                self.state = "ERROR"
```


Navigate to simulate.py and paste the below:

```python

import time
import config
from controller import Controller


class SimulatedPlayer:
    def __init__(self):
        self.active = False

    def start(self, loop_audio):
        self.active = True
        print("SIMULATED audio started; repeat playlist:", loop_audio)

    def poll(self):
        # No files are read. This fake playlist stays active until stopped.
        return self.active

    def stop(self):
        if self.active:
            print("SIMULATED audio stopped")
        self.active = False


def main():
    config.validate()
    delay, duration = config.effective_timing()
    controller = Controller(SimulatedPlayer(), delay, duration, config.LOOP_AUDIO)
    print("Timing simulation only. No sound or GPIO output.")
    print("Delay:", delay, "seconds; playback window:", duration, "seconds")
    started = time.monotonic()
    previous_state = None
    try:
        while True:
            elapsed_ms = int((time.monotonic() - started) * 1000)
            controller.update(elapsed_ms)
            if controller.state != previous_state:
                print("{:.1f}s: {}".format(elapsed_ms / 1000, controller.state))
                previous_state = controller.state
            if controller.state in ("FINISHED", "ERROR"):
                break
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("Simulation interrupted")
    finally:
        controller.cancel()
    if controller.error is not None:
        raise RuntimeError(controller.error)
    print("Simulation exited. The eventual device will remain idle after finishing.")


if __name__ == "__main__":
    main()
```

## Check the bench settings

Open config.py. You should see the below settings (don't worry that loop is under operational settings python reads this in order)

```python
TEST_MODE = True
TEST_START_DELAY_SECONDS = 10
TEST_PLAYBACK_SECONDS = 20
LOOP_AUDIO = True
```


## 4. Run the simulation

Open a New Terminal. Use PowerShell and make sure the terminal
is in TBS_audio_unit. If you see the Python prompt `>>>`, enter `exit()` first.

```powershell
python simulate.py
```

or

```powershell
py simulate.py
```

Expected sequence (times may vary slightly):

```text
Timing simulation only. No sound or GPIO output.
Delay: 10 seconds; playback window: 20 seconds
0.0s: WAITING
SIMULATED audio started; repeat playlist: True
10.0s: PLAYING
SIMULATED audio stopped
30.0s: FINISHED
Simulation exited. The eventual device will remain idle after finishing.
```

There are 10 seconds of waiting followed by 20 seconds of simulated playback.
The desktop demonstration exits at the end. The eventual standalone runner will
remain idle after stopping audio. If you want to stop or have a longer than expected simulation press Ctrl+C to stop.





# STEP 3

Here we are going to prepare and test some voice recordings in Audacity and export them for comparison. The intent with this is to determine how much audio we can load onto our very limited boards. We will check the minimum acceptable quality for minimum amount of storage required. **DO NOT CHANGE ANY OF THE PYTHON FILES IN THIS STEP.**
## Create a folder to compare files

Under TBS_audio_unit, create a NEW folder named `audio_tests`.
This keeps comparison exports out of TBS_audio, which is reserved for the real
device playlist. It should look like the below:

```text
TBS_audio_unit/
    main.py
    config.py
    controller.py
    simulate.py
    TBS_audio/
    audio_tests/
```

## Record a representative sample

Select your microphone and record about 30 seconds of the sort of chatter the
device will play. Include ordinary speaking, a few louder words, and quieter
phrases. Use the same recording for all comparisons.

Adjust microphone input level so loud speech does not overload the recording.
Do not force the input level to maximum. Distortion recorded at the microphone
cannot be removed simply by turning the exported file down.

Listen to the recording. If it is distorted, lower the input level and record
again before continuing.

Save an editable Audacity project named `chatter_master.aup3` in audio_tests.
Saving a project and exporting a playable audio file are separate operations.
Keep this master so later export choices do not require rerecording.


## Prepare a consistent starting level

For this first comparison use a single voice track. Select the audio with Ctrl+A.
Open **Effect > Volume and Compression > Normalize** (menu wording may vary by
Audacity version).

Set peak normalization to **-1.0 dB**, enable removal of DC offset, and apply it.
This is a starting peak level, not a final loudness specification or a guarantee
of maximum speaker output. Normalization alone does not make quiet and loud
phrases equally loud.

## Export the first WAV file

Choose **File > Export Audio** and export to your computer. Set these options:

```text
Filename: chatter_22050.wav
Folder: TBS_audio_unit/audio_tests
Format: WAV (Microsoft)
Channels: Mono
Sample rate: 22050 Hz
Encoding: Signed 16-bit PCM
Export range: Entire project
```

Use PCM, not 32-bit float or an ADPCM option for these comparison files.
Choose Mono in the export options even if your microphone recorded stereo, because we will be using a mono speaker for this build.
The export sample rate controls this file; changing SAMPLE_RATE in config.py
does not convert audio.


## Export smaller comparison files

Export the same project two more times. Keep Mono, Signed 16-bit PCM, and the
same export range. Change only the filename and sample rate:

| Filename | Sample rate |
| --- | --- |
| chatter_16000.wav | 16000 Hz |
| chatter_8000.wav | 8000 Hz |

Do not overwrite the master or repeatedly convert the previous export. Export
each version from the same master project.

## Listen and compare

Play each exported WAV on your computer at the same playback-volume setting.
Listen for intelligibility, muffled speech, and whether the chatter still sounds
acceptable for the intended use. This is a preliminary quality comparison;
the small speaker and enclosure must be tested later.

In File Explorer, right-click each WAV and open Properties. Record **Size** in
bytes, not Size on disk. PCM file size is approximately:

```text
bytes = duration_seconds × sample_rate × channels × bytes_per_sample

For mono, 16-bit PCM:
bytes = duration_seconds × sample_rate × 2
```

WAV headers and metadata add a small amount. For exactly 30 seconds:

| Sample rate | Approximate audio bytes | Decimal MB per minute |
| --- | ---: | ---: |
| 22050 Hz | 1,323,000 | 2.646 |
| 16000 Hz | 960,000 | 1.920 |
| 8000 Hz | 480,000 | 0.960 |

These are calculated PCM sizes, not measurements of your board's free storage.
At a fixed PCM format, quiet audio occupies as much space as loud audio.

Copy this table into your notes and complete it:

| File              | Duration | Size in kbytes | Voice acceptable? |
| ----------------- | -------- | -------------- | ----------------- |
| chatter_22050.wav | 9.5      | 411kb          | yes               |
| chatter_16000.wav | 9.5      | 300kb          | yes               |
| chatter_8000.wav  | 9.5      | 158kb          | no                |
As you can see for me I am willing to accept the 16khz file and it reduces the storage requirement significantly. I will have to test the audio again when we complete the physical set up.





# STEP 4

Here we are going to check our exported WAV files in Python before building the
audio output. The checker will locate the actual audio data and verify the format.
It will not assume every WAV header is 44 bytes. **This step does not play sound.**

We do need to make some changes either here or after we test the audio with the physical components. 
- REPLACE one existing line in config.py: ***SAMPLE_RATE = 22050 becomes 16000***. It sets the accepted WAV sample rate; it does not convert files or establish hardware compatibility.

## Update the existing sample-rate setting

Open config.py. Find this EXISTING line:

```python
SAMPLE_RATE = 22050
```

REPLACE it with the below, then save with Ctrl+S. Do not add a an additional line.

```python
SAMPLE_RATE = 16000
```

If you run main.py again, Candidate sample rate (Hz) will now print 16000.

## Create wav_reader.py

In TBS_audio_unit, create wav_reader.py beside config.py.
Paste the entire block below **INTO THE FILE, NOT THE TERMINAL**, then save.

```python
"""Inspect ordinary RIFF/WAVE PCM files without loading audio into memory."""

import struct


def _read_exact(source, count):
    data = source.read(count)
    if len(data) != count:
        raise ValueError("Truncated WAV file")
    return data


def inspect_wav(path, expected_rate):
    """Return validated metadata, data offset, and data size. No playback."""
    with open(path, "rb") as source:
        source.seek(0, 2)
        file_size = source.tell()
        source.seek(0)
        header = _read_exact(source, 12)
        if header[:4] != b"RIFF" or header[8:] != b"WAVE":
            raise ValueError("Expected a RIFF/WAVE file")
        riff_end = 8 + struct.unpack("<I", header[4:8])[0]
        if riff_end < 12 or riff_end > file_size:
            raise ValueError("Invalid or truncated RIFF size")

        audio_format = None
        data_offset = None
        data_size = None
        position = 12
        while position < riff_end:
            if riff_end - position < 8:
                raise ValueError("Incomplete WAV chunk header")
            source.seek(position)
            chunk_header = _read_exact(source, 8)
            chunk_id = chunk_header[:4]
            chunk_size = struct.unpack("<I", chunk_header[4:])[0]
            payload = position + 8
            next_position = payload + chunk_size + (chunk_size % 2)
            if next_position > riff_end:
                raise ValueError("WAV chunk extends beyond RIFF boundary")

            if chunk_id == b"fmt ":
                if audio_format is not None or chunk_size < 16:
                    raise ValueError("Duplicate or incomplete fmt chunk")
                audio_format = struct.unpack("<HHIIHH", _read_exact(source, 16))
            elif chunk_id == b"data":
                if data_offset is not None:
                    raise ValueError("Multiple data chunks are not supported")
                data_offset = payload
                data_size = chunk_size
            # Skip unknown chunks and their odd-length padding without reading
            # their payloads. Audio itself is also skipped during inspection.
            position = next_position

        if audio_format is None or data_offset is None:
            raise ValueError("Missing fmt or data chunk")
        encoding, channels, rate, byte_rate, alignment, bits = audio_format
        if encoding != 1:
            raise ValueError("Expected ordinary PCM WAV (format tag 1)")
        if channels != 1 or bits != 16:
            raise ValueError("Expected mono, signed 16-bit PCM")
        if rate != expected_rate:
            raise ValueError("Sample rate mismatch: file {} Hz, config {} Hz".format(
                rate, expected_rate))
        if alignment != 2 or byte_rate != rate * 2:
            raise ValueError("Inconsistent PCM block alignment or byte rate")
        if data_size == 0 or data_size % alignment:
            raise ValueError("Empty audio or incomplete PCM frame")
        return {
            "sample_rate": rate,
            "channels": channels,
            "bits": bits,
            "data_offset": data_offset,
            "data_size": data_size,
            "duration_seconds": data_size / byte_rate,
            "file_size": file_size,
        }
```

## Create inspect_wav.py

Create inspect_wav.py in the same folder. Paste the below into that new file
and save. This command-line runner is for desktop testing.

```python
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
```

## Check the 16 kHz export

Your project should now include:

```text
TBS_audio_unit/
    main.py
    config.py
    controller.py
    simulate.py
    wav_reader.py
    inspect_wav.py
    TBS_audio/
    audio_tests/
        chatter_master.aup3
        chatter_22050.wav
        chatter_16000.wav
        chatter_8000.wav
```

Open a PowerShell terminal in TBS_audio_unit and run:

```powershell
py inspect_wav.py "audio_tests/chatter_16000.wav"
```

or
```powershell
python inspect_wav.py "audio_tests/chatter_16000.wav"
```


Expected return should be similar to this (adjusted for your metadata): 
```text
WAV CHECK PASSED
Sample rate (Hz): 16000
Channels: 1
Bits per sample: 16
Audio starts at byte: 44
Audio bytes: 306058
Duration (seconds): 9.564
Total file bytes: 306102
Inspection only. No sound is played.
```

**If you got nothing back it just moved on to the next line. Go back into the new files you created and Ctl+S to ensure they saved.**

## Check that a different sample rate is rejected

Run this on the earlier comparison file without editing config.py:

```powershell
py inspect_wav.py "audio_tests/chatter_22050.wav"
```

Expected return:

```text
WAV CHECK FAILED: Sample rate mismatch: file 22050 Hz, config 16000 Hz
```

This is an intentional rejection. The file is not necessarily damaged; it just doesn't
match our selected rate. Similarly, the 8000 Hz comparison should fail with
its own rate mismatch. Leave SAMPLE_RATE at 16000 afterward.

## What the checker validates

It checks RIFF/WAVE identification, chunk boundaries, format and audio-data
chunks, PCM format tag 1, mono 16-bit samples, the selected rate, consistent byte
rate/frame size, and a nonempty whole number of audio frames. Unknown metadata
chunks are skipped with their alignment padding. Audio is not loaded in full.

It deliberately rejects compressed WAV, float WAV, WAVE_FORMAT_EXTENSIBLE, and
multiple data chunks. If an Audacity export fails, report the message rather than
changing the validator to accept it blindly. The WAV filename extension alone
does not establish encoding.


# STEP 5

Here we are going to prepare the real audio folder and check the playlist in the
order it will be played. **This step checks the files; it does not play sound.**

## Copy the accepted audio into TBS_audio

In File Explorer, COPY audio_tests/chatter_16000.wav into TBS_audio.
Rename the copied file to `001.wav`. Keep the original comparison export and
editable master in audio_tests.

For additional distinct recordings, export each as mono, signed 16-bit PCM,
16000 Hz, then place it in TBS_audio with the next number:

```text
001.wav
002.wav
003.wav
```

Only 001.wav is needed to complete this step. Do not duplicate the same recording
just to fill the folder; repeating a playlist does not require duplicate files.
Do not put the rejected 8000 Hz or the 22050 Hz comparison into this folder.

Use equal-width numbers, such as 001 through 999, so filename sorting matches
the intended order. Keep only playlist audio in this folder. The checker ignores
non-WAV names, but the master and comparison files still belong in audio_tests.

## Create playlist.py

Create playlist.py beside config.py in TBS_audio_unit.
Paste the complete block below **INTO THE FILE, NOT THE TERMINAL**, then save.

```python
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
```

## Create check_playlist.py

Create check_playlist.py in the same folder. Paste the below into it and save.

```python
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
```

## Run the playlist check

Save all files. Open PowerShell in TBS_audio_unit and run:

```powershell
python check_playlist.py
```

Or:

```powershell
py check_playlist.py
```

It should look something like this, but the numbers come from your files:

```text
PLAYLIST CHECK PASSED
Folder: TBS_audio
1. 001.wav | 9.564 seconds | 306102 file bytes
One playlist pass (seconds): 9.564
Total WAV file bytes: 306102
Startup delay (seconds): 10
Playback window (seconds): 20
Repeat playlist: True
Check only. No playback, waiting, or board-storage measurement.
```

With more files, each appears on its own numbered line and the totals increase.
The checker does not wait 10 seconds or simulate a 20-second playback window.
**If you ran into an unspecified location error, it probably happened when you uniquely named your files or directories (differently from mine), go back through and ensure that you all directories and files in the code listed the same as how you have them saved. **

## How the eventual playback will use this

The playlist contains tracks in sorted filename order. The future player will
stream 001.wav, then 002.wav, and so on. With the existing LOOP_AUDIO = True,
it will return to the beginning until the controller's playback window expires.
At expiry it will stop, potentially in the middle of a track.

Only one copy of each track is stored. A 9.564-second recording can be repeated
for a much longer session without creating copies to fill that session.
This checker does not yet implement streaming, looping, or the controller/player
connection. Those are future code additions, not behavior verified in this step.

All candidate WAVs are validated before a playlist is returned. One invalid file
fails the entire check, with the filename included in the message. No files are
deleted, converted, or silently skipped for failing validation.

# STEP 6

Here we are going to connect one RP2040 board to Windows and check the firmware
and storage it currently exposes. We will use that information to select the
firmware for the audio player. **This step does not install firmware or play sound.**

## Install mpremote on Windows

In VS Code, open PowerShell in TBS_audio_unit. Run:

```powershell
python -m pip install --user mpremote
```

or

```powershell
py -m pip install --user mpremote
```

Use one command, not both. Internet is required for this package installation.

Check the installation:

```powershell
python -m mpremote --help
```

Expected: command help. This confirms the Windows tool is installed, not that
the board is connected or has compatible firmware.


## Create board_info.py

Create board_info.py beside config.py. Paste the complete block below **INTO THE
FILE, NOT THE TERMINAL**, then save.

```python
"""Run on the board through mpremote, not directly with desktop Python."""

import sys


def main():
    if sys.implementation.name != "micropython":
        print("Run this script ON THE BOARD using mpremote run board_info.py.")
        return

    import os
    import machine

    print("BOARD DIAGNOSTIC")
    print("Python version:", sys.version)
    print("Implementation:", sys.implementation)
    print("Firmware-reported board:", os.uname())
    print("I2S class available:", hasattr(machine, "I2S"))
    print("Current directory:", os.getcwd())
    print("Root entries:", os.listdir("/"))
    stats = os.statvfs("/")
    unit = stats[1]
    total = unit * stats[2]
    free = unit * stats[3]
    available = unit * stats[4]
    print("Filesystem total bytes:", total)
    print("Filesystem free bytes:", free)
    print("Filesystem available bytes:", available)
    print("Filesystem total MiB: {:.3f}".format(total / (1024 * 1024)))
    print("Filesystem available MiB: {:.3f}".format(available / (1024 * 1024)))
    print("Reported filesystem size is not a physical flash-capacity test.")
    print("I2S class presence does not verify wiring or audio output.")


if __name__ == "__main__":
    main()
```

## Connect one board

Use prototype #1 only. Connect the RP2040's USB-C port directly to your laptop
using a USB data cable. Leave the battery board, amplifier, and speaker disconnected
for this initial test. Do not hold BOOT while connecting: we first want to inspect
the installed firmware, rather than enter its firmware-loading mode.

Close other programs or serial monitors that might already be connected to it.

## Find the board's serial port

Run in PowerShell:

```powershell
python -m mpremote connect list
```

Look for a COM port that appears when the board is connected. If necessary,
compare the list with the board unplugged and then plugged in. Disconnect other
microcontroller boards so you identify the intended device.

The next example uses COM5. **REPLACE COM5 with your actual port.**

```powershell
python -m mpremote connect COM5 run board_info.py
```

mpremote sends this local script to the interpreter for execution without saving
it as a board file. It can interrupt a running program as part of connecting and
executing commands. The diagnostic itself only reads/reports information; it does
not format flash, drive pins, or write files.

## Read the result

The output should begin with BOARD DIAGNOSTIC and include:

- MicroPython version and firmware-reported board identity
- I2S class available: True or False
- Existing files/folders at the root
- Total, free, and available filesystem bytes and MiB

Do not expect a particular board name or storage total yet. The identity comes
from firmware and does not independently identify the physical board revision.

Filesystem capacity is controlled by the firmware configuration and is different
from the flash chip's physical capacity. Free/available space also depends on
existing files. I2S class availability does not prove the pins or amplifier work.
[MicroPython filesystem information](https://docs.micropython.org/en/latest/library/os.html#os.statvfs)

## If no board is found

- Try a known USB data cable and another USB port.
- Check Windows Device Manager for the board's COM port.
- If a drive named RPI-RP2 appears, it is in the RP2040 bootloader, not a running
  MicroPython interpreter. Unplug and reconnect without pressing BOOT. If it
  still only enters the bootloader, firmware may be absent or not starting.
- If the serial port exists but mpremote cannot enter MicroPython, check whether
  another program owns the port. The device may also have different firmware.

If these checks fail, record the symptom plus the board markings and flash-chip
marking (or clear photos). Firmware selection then needs those details before
the connection check can continue. Do not use another manufacturer's UF2 merely
because it advertises 16 MB.


This is the stopping point until we get the actual equipment. Pick up from here




