"""Hardware-independent timing. The runner supplies elapsed milliseconds."""


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