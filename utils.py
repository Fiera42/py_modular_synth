import numpy as np


def mix_audio(*args):
    if len(args) == 0:
        return None

    max_length = max(len(audio) for audio in args)

    mix = np.zeros((max_length, args[0].shape[1]))

    for audio in args:
        normalized_audio = np.pad(audio, ((0, max_length - len(audio)), (0, 0)))
        mix += normalized_audio

    mix_normalized = mix / len(args)

    return mix_normalized.astype(np.float32)
