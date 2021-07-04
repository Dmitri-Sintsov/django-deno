from .deno import DenoApi


class DenoMaps(DenoApi):

    location = '/maps/'
    response_post_schema = {
        'type': 'object',
        'properties': {
            'server': {'type': 'string'},
            'pid': {'type': 'integer'},
            'version': {'type': 'string'},
        }
    }
