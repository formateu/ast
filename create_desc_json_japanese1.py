from __future__ import absolute_import, division, print_function
import argparse
import json
import wave
# from os import listdir
# from os.path import isfile, join
import os
from collections import OrderedDict
import re
from functools import partial

def generate_labels(labels_directory):
    files = [f for f in os.listdir(labels_directory) if os.path.isfile(os.path.join(labels_directory, f))]
    labels_dict = dict()
    for f in files:
        with open(os.path.join(labels_directory, f), 'r') as tabfile:
            for line in tabfile:
                spl = line.split("  ")
                if (len(spl) == 2):
                    labels_dict[spl[0]] = spl[1].rstrip('\n\r.?!')
                else:
                    labels_dict[spl[0]] = spl[2].rstrip('\n\r.?!')
                    labels_dict[spl[1]] = spl[2].rstrip('\n\r.?!')

    for k, v in labels_dict.items():
        labels_dict[k] = re.sub(r'\[.+?\]', '', v)

    return labels_dict

def file_search(path):
    result_list = []
    for root, dirs, files in os.walk(path):
        files = [os.path.join(root, f) for f in files if not f[0] == '.']
        result_list.extend(files)

    return result_list


def main(data_directory, labels_directory, output_file):
    labels = []
    durations = []
    keys = []
    label_dict = generate_labels(labels_directory)
    file_list = file_search(data_directory)

    for fpath in file_list:
        audio = wave.open(fpath)
        duration = float(audio.getnframes()) / audio.getframerate()
        audio.close()

        keys.append(fpath)
        durations.append(duration)
        labels.append(label_dict[fpath.split('/')[-1]])

    # for group in os.listdir(data_directory):
        # if group.startswith('.'):
            # continue
        # speaker_path = os.path.join(data_directory, group)
        # print(speaker_path)
        # for speaker in os.listdir(speaker_path):
            # if speaker.startswith('.'):
                # continue
            # fpath = os.path.join(speaker_path, speaker)
            # for file_id in [f for f in os.listdir(fpath) if os.path.isfile(os.path.join(fpath, f))]:
                # label = label_dict[file_id]
                # audio_file = os.path.join(fpath, file_id)
                # audio = wave.open(audio_file)
                # duration = float(audio.getnframes()) / audio.getframerate()
                # audio.close()

                # keys.append(audio_file)
                # durations.append(duration)
                # labels.append(label_dict[file_id])

    with open(output_file, 'w') as out_file:
        for i in range(len(keys)):
            line = json.dumps({'key': keys[i], 'duration': durations[i], 'text': labels[i]})
            out_file.write(line + '\n')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_directory', type=str,
                        help='Path to data directory')
    parser.add_argument('label_directory', type=str,
                        help='Path to transitions directory')
    parser.add_argument('output_file', type=str,
                        help='Path to output file')
    args = parser.parse_args()
    main(args.data_directory, args.label_directory, args.output_file)
    # print(generate_labels(args.data_directory))
