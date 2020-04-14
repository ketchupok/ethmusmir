# code based on: https://falcon.readthedocs.io/en/stable/user/tutorial.html#first-steps
# adapted by Alex Hofmann (2020)

import os
import falcon

from .audio import AudioStore, Resource

def create_app(audio_store):
    audio_resource = Resource(audio_store)
    api = falcon.API()
    api.add_route('/v1/audio', audio_resource)
    return api


def get_app():
    storage_path = os.environ.get('LOOK_STORAGE_PATH', '.')
    audio_store = AudioStore(storage_path)
    return create_app(audio_store)
