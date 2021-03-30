from .base import Api


class DenoMaps(Api):

    location = '/maps/'
    schema = {
        'server': ['string'],
        'pid': ['int'],
        'version': ['string'],
    }
