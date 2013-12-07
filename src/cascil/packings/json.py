from __future__ import absolute_import
from cascil.registry_manager import register
import json

@register('packing', 'json')
class JsonPacking(object):
    @staticmethod
    def pack(message):
        return json.dumps(message)

    @staticmethod
    def unpack(data):
        return json.loads(data)