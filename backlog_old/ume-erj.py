# -*- coding: utf-8 -*-
"""This module contains functions used to preprocess Data set containing
Japanese people speaking english.

"""
import argparse
import json
import wave
import os
from os.path import isfile, join
import re


def generate_labels(labels_directory):
    files = [f for f in os.listdir(labels_directory) if
             isfile(join(labels_directory, f))]
    labels_dict = dict()
    for f in files:
        with open(os.path.join(labels_directory, f), 'r') as tabfile:
            for line in tabfile:
                spl = line.split("  ")
                if len(spl) == 2:
                    labels_dict[spl[0]] = spl[1].lower()
                else:
                    labels_dict[spl[0]] = spl[2].lower()
                    labels_dict[spl[1]] = spl[2].lower()

    # clean up labels
    # they must consist of characters in char_map
    for k, v in labels_dict.items():
        if '10th' in v:  # found empirically
            labels_dict[k] = v.replace('10th', 'tenth')
        labels_dict[k] = re.sub(r'\[.+?\]', '', labels_dict[k])
        labels_dict[k] = re.sub("[^0-9a-zA-Z ]", "", labels_dict[k])

    return labels_dict


def remove_sentences(labels_dict):
    return {k: v for k, v in labels_dict.items() if ' ' not in v}


def file_search(path):
    result_list = []
    for root, dirs, files in os.walk(path):
        files = [os.path.join(root, f) for f in files if not f[0] == '.']
        result_list.extend(files)

    return result_list


def save_file(output_file, label_dict, file_list):
    labels = []
    durations = []
    keys = []

    for fpath in file_list:
        filename = fpath.split('/')[-1]
        if filename in label_dict:
            audio = wave.open(fpath)
            duration = float(audio.getnframes()) / audio.getframerate()
            audio.close()

            if duration != 0.0:
                keys.append(fpath)
                durations.append(duration)
                labels.append(label_dict[filename])

    with open(output_file, 'w') as out_file:
        for i in range(len(keys)):
            line = json.dumps({'key': keys[i], 'duration': durations[i],
                               'text': labels[i]})
            out_file.write(line + '\n')


def create_data_dicts(train_data_path, valid_data_path, labels_path):
    label_dict = generate_labels(labels_path)
    train_file_list = file_search(train_data_path)
    valid_file_list = file_search(valid_data_path)
    save_file('train_corpus.json', label_dict, train_file_list)
    save_file('valid_corpus.json', label_dict, valid_file_list)


def create_data_dicts_with_split(data_path, labels_path):
    label_dict = generate_labels(labels_path)
    # label_dict = remove_sentences(label_dict)

    # these words caused CTC loss function error
    # caused by too long text or too short audio file
    #     forbidden_files = [
    #   #actually whole JE/TKT directory has been dropped
    #         'W4_053.wav', #JE/TKT/F02
    #         'W1_213.wav', #JE/TKT/F04
    #         'W4_136.wav', #JE/TKT/F02
    #         'W4_145.wav', #JE/TKT/F02
    #         'W4_149.wav', #JE/TKT/F02
    #         'W1_107.wav', #JE/TKT/F04
    #         'W1_067.wav', #JE/TKT/F04
    #         'W4_164.wav', #JE/TKT/F02
    #         'W4_012.wav', #JE/TKT/F02
    #         'W4_107.wav', #JE/TKT/F02
    #         ''
    #     ]

    #     label_copy = label_dict.copy()
    #     for k,v in label_copy.items():
    #         if k in forbidden_files:
    #             label_dict.pop(k)

    # reverse twice to get rid of value repetitions for different keys
    # this is nondeterministic division of the whole set
    # don't have idea how to perform this in elegant way
    # because training set contains big number of words with low repetition
    validation_set = {v: k for k, v in label_dict.items()}
    validation_set = {v: k for k, v in validation_set.items()}
    train_set = {k: label_dict[k] for k in
                 set(label_dict) - set(validation_set)}
    assert (len(train_set) + len(validation_set) == len(label_dict))

    file_list = file_search(data_path)
    save_file('valid_corpus.json', validation_set, file_list)
    save_file('train_corpus.json', train_set, file_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('train_data', type=str,
                        help='Path to train data directory')
    parser.add_argument('label_directory', type=str,
                        help='Path to translations directory')
    parser.add_argument('--with_split', type=bool, default=False,
                        help="If flag is true, train set is split into" +
                             "train and valid parts")
    parser.add_argument('--valid_data', type=str,
                        help='Path to valid data directory')
    args = parser.parse_args()

    if args.with_split:
        create_data_dicts_with_split(args.train_data, args.label_directory)
    else:
        create_data_dicts(args.train_data, args.valid_data,
                          args.label_directory)
