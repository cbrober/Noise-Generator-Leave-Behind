"""Windows/desktop-only timing demonstration. No decoder or hardware access."""

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