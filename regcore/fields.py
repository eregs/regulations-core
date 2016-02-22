import base64
import bz2
import json

from django.db import models
import six


class CompressedJSONField(models.TextField):
    """We store a lot of data redundantly. This field type makes each copy
    much smaller. We need this when inserting hundreds of regtext nodes and
    layer nodes into relational databases, lest we blow the packet size limit
    """
    # Now returning to regularly scheduled class definition
    def to_python(self, value):
        """Convert the string (from the database) into a JSON dictionary"""
        if not isinstance(value, six.text_type):
            return value

        encoding, content = value.split('$', 1)
        encoding = reversed(encoding)
        for encoding_type in encoding:
            if encoding_type == 'j':
                content = json.loads(content)
            elif encoding_type == '6':
                content = base64.decodestring(content)
            elif encoding_type == 'b':
                content = bz2.decompress(content)
        return content

    def from_db_value(self, value, expression, connection, context):
        """Satisfies Django 1.8's custom field types requirements."""
        return self.to_python(value)

    def get_prep_value(self, value):
        """Convert from a JSON dictionary to a database string"""
        value = json.dumps(value)
        encoding = 'j'

        if len(value) > 1000:  # somewhat arbitrary length to start compression
            # check if compressing is smaller
            compressed = base64.encodestring(bz2.compress(value))
            if len(compressed) < len(value):
                encoding += 'b6'
                value = compressed

        return encoding + '$' + value
