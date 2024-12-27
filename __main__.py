# -*- coding: utf-8 -*-
import sounddevice as sd
import numpy as np
from hardware import OutputDevice, InputDevice
from wave_gen import SineWave, LinearSignal, SquareWave, TriangleWave
from utils import mix_audio


def main():
    output_device = OutputDevice(sd.default.device[1])

    C_sinewave = SineWave(
        channels=output_device.channels,
        samplerate=output_device.samplerate,
    )

    control_sine = SineWave(
        channels=output_device.channels,
        samplerate=output_device.samplerate,
        middle_value=1.5,
        frequency=0.3,
        amplitude=0.6,
        upper_limit=1.4,
    )

    control_square = SquareWave(
        channels=output_device.channels,
        samplerate=output_device.samplerate,
        frequency=0.1,
        amplitude=2,
    )

    linear_signal = LinearSignal(
        middle_value=0.5,
        amplitude=1.8,
        frequency=0.15,
        channels=output_device.channels,
        samplerate=output_device.samplerate,
        upper_limit=1.4,
        lower_limit=-10000,
    )

    triangle_wave = TriangleWave(
        amplitude=1,
        shape=1,
        channels=output_device.channels,
        samplerate=output_device.samplerate,
    )

    input_device = InputDevice(sd.default.device[0])
    input_device.start()

    frame_size = 1024

    try:
        while True:
            if linear_signal.is_upper():
                linear_signal.reset_phase()

            linear = linear_signal.get(frame_size)
            square_control = control_square.get(frame_size)
            control = control_sine.get(
                frame_size, frequency_control=square_control, amplitude_control=linear
            )
            sine_audio = C_sinewave.get(frame_size, frequency_control=control)
            device_audio = input_device.get(frame_size)

            triangle = triangle_wave.get(frame_size)
            # print(triangle)

            # mix = mix_audio(sine_audio, device_audio)
            mix = sine_audio

            output_device.play_sound(mix)
    except KeyboardInterrupt:
        input_device.stop()
        output_device.close()


if __name__ == "__main__":
    main()
