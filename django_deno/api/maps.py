from .base import JsonApi


class DenoMaps(JsonApi):

    location = '/maps/'
    target_schema = {
        'type': 'object',
        'properties': {
            'server': {'type': 'string'},
            'pid': {'type': 'integer'},
            'version': {'type': 'string'},
        }
    }
