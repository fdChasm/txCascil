from __future__ import absolute_import
from cascil.registry_manager import register
import clj

@register('packing', 'edn')
class EdnPacking(object):
    @staticmethod
    def pack(message):
        return clj.dumps(message)

    @staticmethod
    def unpack(data):
        return clj.loads(data)
