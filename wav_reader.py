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