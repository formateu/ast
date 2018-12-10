from sys import argv
import os
from collections import OrderedDict
import numpy as np
from functools import partial
from spectrogram import pretty_spectrogram
from scipy.io import wavfile
import cv2


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

    np.save('X_' + out_file_suffix, X)
    np.save('y_' + out_file_suffix, y)


def preprocess_all():
    preprocess_data('X_train.npy')
    print("training data successfully normalized")
    preprocess_data('X_test.npy')
    print("testing data successfully normalized")


def preprocess_data(f_name):
    data = np.load(f_name)
    
    mean_x = 0
    mean_y = 0
    for i in range(data.shape[0]):
        mean_x  = mean_x + data[i].shape[0]
        mean_y = mean_y + data[i].shape[1]

    mean_x /= data.shape[0]
    mean_y /= data.shape[0]

    for i in range(data.shape[0]):
         data[i] = np.array(cv2.resize(data[i], (int(mean_y) , int(mean_x)), interpolation = cv2.INTER_CUBIC))
    
    data = np.array(data.tolist())
    data -= np.mean(data, axis = 0)
    data /= np.std(data, axis = 0)
    np.save(f_name + '_normalized', data)

def load_data():
    x_train = np.load('X_train_normalized.npy')
    y_train = np.load('y_train.npy')
    x_test =  np.load('X_test_normalized.npy')
    y_test = np.load('y_test.npy')
        
    return (x_train, y_train), (x_test, y_test)

    
if __name__ == "__main__":
#     set_home = argv[1]
#     load_raw_data_to_file(set_home, 'testing_list.txt', 'train')
#     print("training data loaded successfully")
#     load_raw_data_to_file(set_home, 'validation_list.txt', 'test')
#     print("testing data loaded successfully")
# #     print(cv2.__version__)
    preprocess_all()
