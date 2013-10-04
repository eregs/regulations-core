import base64
import bz2

import anyjson
from django.db import models
from django.db.models.fields.subclassing import Creator
from south.modelsinspector import add_introspection_rules


class PatchedSubFieldBase(type):
    """These next bits all related to a bug in django custom fields which
    prevent autodoc from succeeding. Once the associated fix is in our
    version of django, we can uncomment the metaclass line and delete
    PatchedCreator and make_contrib
    https://code.djangoproject.com/ticket/12568"""
    class PatchedCreator(Creator):
        def __get__(self, obj, type=None):
            if obj is None:
                return self
            return obj.__dict__[self.field.name]

    def __new__(cls, name, bases, attrs):
        new_class = super(PatchedSubFieldBase, cls).__new__(cls, name, bases,
                                                            attrs)
        def contrib(self, cls, name):
            if attrs.get('contrib_to_class'):
                func(self, cls, name)
            else:
                super(new_class, self).contribute_to_class(cls, name)
            setattr(cls, self.name, PatchedSubFieldBase.PatchedCreator(self))
        new_class.contribute_to_class = contrib
        return new_class

class CompressedJSONField(models.TextField):
    """We store a lot of data redundantly. This field type makes each copy
    much smaller. We need this when inserting hundreds of regtext nodes and
    layer nodes into relational databases, lest we blow the packet size limit
    """
    __metaclass__ = PatchedSubFieldBase


    # Now returning to regularly scheduled class definition

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

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

add_introspection_rules([], ["^regcore\.fields\.CompressedJSONField"])
