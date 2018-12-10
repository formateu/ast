from sys import argv
import os
from collections import OrderedDict
import numpy as np
from functools import partial
from spectrogram import pretty_spectrogram
from scipy.io import wavfile


def load_raw_data_to_file(file_path, list_file_path, out_file_suffix):
    X_names = np.loadtxt(os.path.join(file_path, list_file_path), dtype=str)
    classes = set(map(lambda x: x.split('/')[0], X_names))
    # sort for reproducibility
    classes = OrderedDict((v, k) for k, v in enumerate(sorted(classes)))
    # class names based on wav file location
    y = np.fromiter(map(lambda x: classes[x.split('/')[0]], X_names), dtype='int')

    fft_size = 2048  # window size for the FFT
    step_size = fft_size / 16  # distance to slide along the window (in time)
    spec_thresh = 4  # threshold for spectrograms (lower filters out more noise)
    make_spectrogram = partial(pretty_spectrogram, fft_size=fft_size, step_size=step_size, log=True, thresh=spec_thresh)
    X = list(map(lambda partial_path: wavfile.read(os.path.join(file_path, partial_path))[1], X_names))
    X = np.array(list(map(lambda wav_content: make_spectrogram(wav_content.astype('float64')), X)))

    np.savetxt('X_' + out_file_suffix, X)
    np.savetxt('y_' + out_file_suffix, y)


if __name__ == "__main__":
    set_home = argv[1]
    load_raw_data_to_file(set_home, 'testing_list.txt', 'train')
    load_raw_data_to_file(set_home, 'validation_list.txt', 'test')
