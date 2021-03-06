# code based on: https://falcon.readthedocs.io/en/stable/user/tutorial.html#first-steps
# adapted by Alex Hofmann (2020)
import io
import mimetypes
import os
import uuid

import falcon
import msgpack
import json
import logging
import scipy.io.wavfile as wav

from .fieldRecordingSegmentation.speech_music_parts import find_speech_music_parts

# General Settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', filename='EthMusMIR_server.log')
mimetypes.init()
mimetypes.add_type('audio/wav', '.wav')
ALLOWED_AUDIO_TYPES = (
    'audio/wav',
    #'audio/mp3',
)

def validate_audio_type(req, resp, resource, params):
    if req.content_type not in ALLOWED_AUDIO_TYPES:
        msg = 'Audio type not allowed. Must be WAV or MP3'
        raise falcon.HTTPBadRequest('Bad request', msg)


# Server functionality
class Resource(object):

    def __init__(self, audio_store):
        self._audio_store = audio_store

    def on_get(self, req, resp):
        doc = {
            'audio': [
                {
                    'href': '/audio/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.wav -- dummy'
                }
            ]
        }

        resp.data = msgpack.packb(doc, use_bin_type=True)
        resp.content_type = falcon.MEDIA_MSGPACK
        resp.status = falcon.HTTP_200


    @falcon.before(validate_audio_type) # hook
    def on_post(self, req, resp):
        logging.info('Received a POST request.')
        name = self._audio_store.save(req.stream, req.content_type)
        audio_analysis = AudioAnalysis(name, self._audio_store._storage_path)
        audio_result = audio_analysis.analyse()
        resp.body = json.dumps(audio_result, ensure_ascii=False)
        resp.status = falcon.HTTP_201
        resp.location = '/v1/audio/' + name
        logging.info('Returned "201 created" MIR analysis results.')


#  storing the received audio file (TODO: make it temporarily)
class AudioStore(object):

    _CHUNK_SIZE_BYTES = 4096

    def __init__(self, storage_path, uuidgen=uuid.uuid4, fopen=io.open):
        self._storage_path = storage_path
        self._uuidgen = uuidgen
        self._fopen = fopen

    def save(self, audio_stream, audio_content_type):
        logging.info('Storing attached file. (collecting chunks..)')
        ext = mimetypes.guess_extension(audio_content_type)
        name = '{uuid}{ext}'.format(uuid=self._uuidgen(), ext=ext)
        audio_path = os.path.join(self._storage_path, name)
        with self._fopen(audio_path, 'wb') as audio_file:
        # with io.open(audio_path, 'wb') as audio_file:
            while True:
                chunk = audio_stream.read(self._CHUNK_SIZE_BYTES)
                if not chunk:
                    break

                audio_file.write(chunk)
        logging.info('File received and temporarily stored.')
        return name


class AudioAnalysis(object):

    def __init__(self, name, path):
        self._name = name
        self._storage_path = path

    def analyse(self):
        logging.info('Starting MIR analysis.')
        try:
            (rate, sig) = wav.read(self._storage_path + self._name)
            recording_parts = find_speech_music_parts(self._storage_path + self._name)
            track = {}
            track['duration'] = len(sig)/rate
            track['tempo'] = 'nan'
            track['parts'] = recording_parts
            analysis = {'track' : track}
            return analysis
        except:
            logging.warning('Error while opening and analyzing audio file! (Only WAV files supported.)')
            analysis = {}
            return analysis
