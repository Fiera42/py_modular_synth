# -*- coding: utf-8 -*-
import numpy as np


class Wave(object):
    def __init__(
        self,
        frequency=261.63,
        amplitude=1,
        middle_value=0,
        phase=0,
        channels=1,
        samplerate=44100,
        lower_limit=-10000,
        upper_limit=10000,
    ):
        self.frequency = frequency
        self.amplitude = amplitude
        self.middle_value = middle_value
        self.phase = phase
        self.channels = channels
        self.samplerate = samplerate
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def get_phases(self, frames, control=None):
        t = np.arange(frames) / self.samplerate

        if control is None:
            phase_offset = 2 * np.pi * self.frequency * t + self.phase
        else:
            control = control[:, 0]
            frequency_modulation = np.interp(t, np.arange(len(control)), control)
            phase_increment = (self.frequency * frequency_modulation) / self.samplerate
            phase_offset = np.cumsum(phase_increment) * 2 * np.pi
            phase_offset += self.phase

        # Mise à jour de la phase
        self.phase = phase_offset[-1]

        return phase_offset

    def process_signal(self, signal, control=None):
        output_signal = self.apply_amplitude_control(signal, control)
        output_signal = self.apply_limit(output_signal)
        return self.shape_to_channel(output_signal).astype(np.float32)

    def apply_limit(self, signal):
        output_signal = np.clip(np.copy(signal), self.lower_limit, self.upper_limit)

        return output_signal

    def apply_amplitude_control(self, signal, control=None):
        if control is None:
            return signal

        if control.ndim < signal.ndim:
            return signal * np.tile(control, (1, signal.shape[1]))
        elif control.ndim > signal.ndim:
            control = control[:, 0]
            return signal * control
        else:
            return signal * control

    def shape_to_channel(self, signal):
        return np.tile(signal[:, np.newaxis], (1, self.channels))

    def reset_phase(self, new_phase=0):
        self.phase = new_phase


class SineWave(Wave):
    def get(self, frames, frequency_control=None, amplitude_control=None):
        phases = self.get_phases(frames, frequency_control)
        signal = self.middle_value + self.amplitude * np.sin(phases)
        return self.process_signal(signal, amplitude_control)


class SquareWave(Wave):
    def get(self, frames, frequency_control=None, amplitude_control=None):
        phases = self.get_phases(frames, frequency_control)
        signal = self.middle_value + self.amplitude * np.sign(np.sin(phases))
        return self.process_signal(signal, amplitude_control)


class TriangleWave(Wave):
    def __init__(self, shape=0.5, **kwargs):
        super().__init__(**kwargs)
        self.shape = shape

    def get(self, frames, frequency_control=None, amplitude_control=None):
        # Calcul des phases
        phases = self.get_phases(frames, frequency_control)

        # Calcul de la valeur de crête du triangle en fonction de la forme
        peak_value = 1 - 2 * abs(self.shape - 0.5)

        # Génération de l'onde triangulaire
        signal = peak_value * (2 * np.abs((phases / np.pi) % 2 - 1) - 1)

        return self.process_signal(signal, amplitude_control)


class LinearSignal(Wave):
    def get(self, frames, frequency_control=None, amplitude_control=None):
        phase_values = self.get_phases(frames, frequency_control)
        signal = self.middle_value + self.amplitude * phase_values
        return self.process_signal(signal, amplitude_control)

    def is_upper(self):
        if self.upper_limit is None:
            return False

        time = self.phase / (2 * np.pi * self.frequency)
        signal_value = self.middle_value + self.amplitude * time
        return signal_value >= self.upper_limit

    def is_lower(self):
        if self.lower_limit is None:
            return False

        time = self.phase / (2 * np.pi * self.frequency)
        signal_value = self.middle_value + self.amplitude * time
        return signal_value <= self.lower_limit
