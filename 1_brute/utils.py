import os
import numpy as np
from scipy.io.wavfile import read
from scipy.signal import spectrogram
import matplotlib.pyplot as plt

def load_all_wavs(root_path):
    loaded_wavs = []
    rates = []
    for root, _, filenames in os.walk(root_path):
        for fname in filenames:
            file_path = os.path.join(root, fname)
            rate, data = read(file_path)
            loaded_wavs.append(data)
            rates.append(rate)

    print(len(loaded_wavs))


def audio_to_spectrogram(rates, data):
    assert(rates.shape[0] == data.shape[0])
    for rate, wav in zip(rates, data):
        f, t, Sxx = spectrogram(wav, 1/rate)
        #show pretty spectrograms
        # plt.pcolormesh(t, f, Sxx)
        # plt.ylabel('Frequency [Hz]')
        # plt.xlabel('Time [sec]')
        # plt.show()

def load_dataset():
    dataset = {}
    jap_rates, jap_speakers = load_all_wavs('./ume-erj/wav/JE')
    eng_rates, eng_speakers = load_all_wavs('./ume-erj/wav/AE')
    # Model speakers for validation
    mdl_rates, mdl_speakers = load_all_wavs('./ume-erj/wav/MDL')

    dataset["jap_rates"] = jap_rates
    dataset["jap_speakers"] = jap_speakers
    dataset["eng_rates"] = eng_rates
    dataset["eng_speakers"] = eng_speakers
    dataset["mdl_rates"] = eng_rates
    dataset["mdl_speakers"] = eng_speakers

    return dataset

if __name__ == '__main__':
    dataset = load_dataset()

    jap_rates = dataset["jap_rates"]
    jap_speakers = dataset["jap_speakers"]
    audio_to_spectrogram(jap_rates, jap_speakers)
