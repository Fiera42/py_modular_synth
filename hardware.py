# -*- coding: utf-8 -*-

import sounddevice as sd


class OutputDevice(object):
    def __init__(self, deviceIndex):
        sd.check_output_settings(deviceIndex)

        self.index = deviceIndex
        self.info = sd.query_devices(self.index, "output")
        self.samplerate = int(self.info["default_samplerate"])
        self.channels = self.info["max_output_channels"]
        self.audio_stream = sd.OutputStream(
            samplerate=self.samplerate,
            device=self.index,
            channels=self.channels,
        )
        self.audio_stream.start()

    def play_sound(self, data):
        self.audio_stream.write(data)

    def close(self):
        self.audio_stream.close()

    def available(self):
        return self.audio_stream.write_available


class InputDevice(object):
    def __init__(self, deviceIndex):
        sd.check_input_settings(deviceIndex)

        self.index = deviceIndex
        self.info = sd.query_devices(self.index, "input")
        self.samplerate = int(self.info["default_samplerate"])
        self.channels = self.info["max_input_channels"]

        self.audio_stream = sd.InputStream(
            samplerate=self.samplerate,
            device=self.index,
            channels=self.channels,
        )

    def start(self):
        self.audio_stream.start()

    def stop(self):
        self.audio_stream.stop()

    def get(self, frames=None):
        if not frames:
            frames = self.available()

        audio_data, _ = self.audio_stream.read(frames)
        return audio_data

    def available(self):
        return self.audio_stream.read_available
