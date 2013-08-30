import base64
import bz2

import anyjson
from django.db import models
from south.modelsinspector import add_introspection_rules


class CompressedJSONField(models.TextField):
    """We store a lot of data redundantly. This field type makes each copy
    much smaller"""

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if not isinstance(value, str) and not isinstance(value, unicode):
            return value

        encoding, content = value.split('$', 1)
        encoding = reversed(encoding)
        for encoding_type in encoding:
            if encoding_type == 'j':
                content = anyjson.deserialize(content)
            elif encoding_type == '6':
                content = base64.decodestring(content)
            elif encoding_type == 'b':
                content = bz2.decompress(content)
        return content

    def get_prep_value(self, value):
        value = anyjson.serialize(value)
        encoding = 'j'

        if len(value) > 1000: # somewhat arbitrary length to start compression
            # check if compressing is smaller
            compressed = base64.encodestring(bz2.compress(value))
            if len(compressed) < len(value):
                encoding += 'b6'
                value = compressed

        return encoding + '$' + value

add_introspection_rules([], ["^regcore\.fields\.CompressedJSONField"])
