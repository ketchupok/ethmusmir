import io
import mimetypes
import os
import uuid

import falcon
import msgpack
import json

import scipy.io.wavfile as wav

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

class Resource(object):

    def __init__(self, audio_store):
        self._audio_store = audio_store

    def on_get(self, req, resp):
        doc = {
            'images': [
                {
                    'href': '/audio/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.png'
                }
            ]
        }

        resp.data = msgpack.packb(doc, use_bin_type=True)
        resp.content_type = falcon.MEDIA_MSGPACK
        resp.status = falcon.HTTP_200

    @falcon.before(validate_audio_type) # hook
    def on_post(self, req, resp):
        name = self._audio_store.save(req.stream, req.content_type)
        audio_analysis = AudioAnalysis(name, self._audio_store._storage_path)
        audio_result = audio_analysis.analyse()
        resp.body = json.dumps(audio_result, ensure_ascii=False)
        resp.status = falcon.HTTP_201
        resp.location = '/audio/' + name


class AudioStore(object):

    _CHUNK_SIZE_BYTES = 4096

    def __init__(self, storage_path, uuidgen=uuid.uuid4, fopen=io.open):
        self._storage_path = storage_path
        self._uuidgen = uuidgen
        self._fopen = fopen

    def save(self, audio_stream, audio_content_type):
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

        return name

class AudioAnalysis(object):

    def __init__(self, name, path):
        self._name = name
        self._storage_path = path

    def analyse(self):
        (rate, sig) = wav.read(self._storage_path + self._name)

            #   "track": {
            #     "duration": 255.34898,
            #     "sample_md5": "",
            #     "offset_seconds": 0,
            #     "window_seconds": 0,
            #     "analysis_sample_rate": 22050,
            #     "analysis_channels": 1,
            #     "end_of_fade_in": 0,
            #     "start_of_fade_out": 251.73333,
            #     "loudness": -11.84,
            #     "tempo": 98.002,
            #     "tempo_confidence": 0.423,
            #     "time_signature": 4,
            #     "time_signature_confidence": 1,
            #     "key": 5,
            #     "key_confidence": 0.36,
            #     "mode": 0,
            #     "mode_confidence": 0.414,
            #     "codestring": "eJxVnAmS5DgOBL-ST-B9_P9j4x7M6qoxW9tpsZQSCeI...",
            #     "code_version": 3.15,
            #     "echoprintstring": "eJzlvQmSHDmStHslxw4cB-v9j_A-tahhVKV0IH9...",
            #     "echoprint_version": 4.12,
            #     "synchstring": "eJx1mIlx7ToORFNRCCK455_YoE9Dtt-vmrKsK3EBsTY...",
            #     "synch_version": 1,
            #     "rhythmstring": "eJyNXAmOLT2r28pZQuZh_xv7g21Iqu_3pCd160xV...",
            #     "rhythm_version": 1
            #   }
            # }
        track = {}
        track['duration'] = len(sig)/rate
        track['tempo'] = 'nan'
        analysis = {'track' : track}
        return analysis
