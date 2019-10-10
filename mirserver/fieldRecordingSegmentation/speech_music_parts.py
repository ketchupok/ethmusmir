'''
Algorithm by:
M. Marolt, C. Bohak, A. Kavčič, and M. Pesek, "Automatic segmentation of ethnomusicological field recordings," Applied sciences, vol. 9, iss. 3, pp. 1-12, 2019.

Code based on: https://github.com/matijama/field-recording-segmentation
Adaptations: Alex Hofmann, Peter Knees
'''

import tensorflow as tf
import librosa
import math
import numpy as np
import configparser
from termcolor import colored


config = {
    "sampling_rate": 22050,
    "feature_step_size": 315,
    "label_sampling_rate": 1, # 1 label generated per seconds
    "max_duration": None, # max duration of audio files used (in seconds)
    "mel_bands": 80,
    "mel_min": 30, # in hertz
    "mel_max": 8000, # in hertz
    "model_block_length_s": 2, # seconds
    "model_path": "mirserver/fieldRecordingSegmentation/trained-model",
    "segment_file_path": "data/segments", # output dir to store music segments
    "min_segment_length": 2, # minimum number of continuous segments that lead to splitting/output of audio files
    "min_speech_certainty": 0.5, # minimum probability required to consider a segment as speech segment
    "query_segments_path": "data/query_segments"
}

def calc_features(file_name):
    """
    calculate audio features as required for SeFIRe
    :param file_name: name of the file that should be calculated
    :return: 2D np.array
    """
    # get audio series converted to mono and perform normalization
    y, _ = librosa.load(file_name, sr=config["sampling_rate"], mono=True, duration=config["max_duration"])
    y = y / max(abs(y)) * 0.9

    fftsize = 1024  # window size for fourier transformation
    stepsize = config["feature_step_size"]  # distance between origin of value used for STFT column

    minF = 0
    maxF = 11025

    D = np.abs(librosa.stft(y, fftsize, stepsize)) # short time fourier transformation
    freqs = librosa.fft_frequencies(config["sampling_rate"], fftsize) # get sample frequencies
    D = D[np.logical_and(freqs >= minF, freqs <= maxF), :] # we are not interested in all frequency values
    D = D.transpose()

    return D


def get_segment_labels(file_name, model_path = config["model_path"]):
    """
    uses the sefire tensorflow model to predict probabilities for the 4 target classes
    makes config["label_sampling_rate"] predictions per second
    :param file_name: name of the audio file
    :param model_path: path to the tensorflow model
    :return: 2D np.array, dim0: 2s block of the audio file, dim1: softmax prediction-probabilities in the
    following order: <solo singing, choir singing, instrumental, speech>
    """
    tf.reset_default_graph() # reset any previous tf graph changes

    D = np.transpose(calc_features(file_name)) # transpose to match model input

    adapted_sr = config["sampling_rate"]/config["feature_step_size"]
    # step size between labels and values used as input for one label
    label_step_size = adapted_sr/config["label_sampling_rate"]
    block_len = int(adapted_sr*config["model_block_length_s"])

    with tf.Session(graph=tf.Graph()) as sess:
        # load model and extract in/out tensors
        # note: this is performed per file and could be improved with e.g. a singleton)
        tf.saved_model.loader.load(sess, ['scoring-tag'], model_path)
        x_input = sess.graph.get_tensor_by_name("xinput:0")
        y_pred = sess.graph.get_tensor_by_name("predictions:0")
        j = 0
        i = 0.0
        preds = None

        # score batches of 200 frames, add them to preds array
        while i < D.shape[1] - block_len:

            inp = np.zeros([200, D.shape[0], block_len, 1])
            for k in range(0, 200):
                inp[k, :, :, 0] = D[:, int(i):int(i) + block_len]
                i = i + label_step_size
                if i > D.shape[1] - block_len:
                    break

            inp = inp[:k + 1, :, :, :]
            all_pred = sess.run(y_pred, feed_dict={x_input: inp})

            if (preds is None):
                preds = np.zeros((math.ceil(D.shape[1] / label_step_size), all_pred.shape[1]))
            preds[j:j + k + 1, :] = all_pred
            j += k + 1

    preds = preds[:j, :]

    return preds

def remove_repeated_content(time_content):
    '''
    after algorithm detects the type of audio material every second, we are
    only interested in the times where the material changes
    '''
    audio_len = time_content[-1] # last second that was analysed
    last_type = None
    filtered_time_content = []
    for i in time_content:
        if i[1] == last_type:
            last_type = i[1]
        else:
            filtered_time_content.append(i)
            last_type = i[1]
    ending_element = [audio_len[0]+1, 'end']
    filtered_time_content.append(ending_element)
    return filtered_time_content

def export_parts(time_content):
    '''
    bring array of parts into a dict format for json export
    '''
    parts = []
    for x,i in enumerate(time_content[:-1]):
        start = i[0]
        duration = time_content[x+1][0] - start
        content = i[1]
        part = {"start": start,
                "duration": duration,
                "content": content}
        parts.append(part)
    return parts

def find_speech_music_parts(file_name):
    '''
    Main function to return parts of a longer audio file with annotations of
    either ['solo singing', 'choir singing', 'instrumental', 'speech']
    '''
    segment_predictions = get_segment_labels(file_name, config['model_path'])
    categories = ['solo singing', 'choir singing', 'instrumental', 'speech']
    i = 0
    time_content = []
    for frame_prob in segment_predictions:
        time = i * config['label_sampling_rate']
        content = categories[frame_prob.argmax()]
        print(str(time) + ': ' + colored(content, 'green'))
        time_content.append([time, content])
        i = i+ 1
    time_content = remove_repeated_content(time_content)
    parts = export_parts(time_content)
    return(parts)
