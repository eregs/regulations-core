from haystack import indexes

from regcore import models


class DocumentIndex(indexes.Indexable, indexes.SearchIndex):
    """Search index used by Haystack"""
    doc_type = indexes.CharField(model_attr='doc_type')
    version = indexes.CharField(model_attr='version', null=True)
    label_string = indexes.CharField(model_attr='label_string')
    text = indexes.CharField(model_attr='text')
    is_root = indexes.BooleanField(model_attr='root')
    is_subpart = indexes.BooleanField()
    title = indexes.MultiValueField()

    regulation = indexes.CharField(model_attr='label_string')
    text = indexes.CharField(document=True, use_template=True)

    def prepare_regulation(self, obj):
        return obj.label_string.split('-')[0]

    def prepare_is_subpart(self, obj):
        return (
            'Subpart' in obj.label_string or
            'Subjgrp' in obj.label_string
        )

    def prepare_title(self, obj):
        """For compatibility reasons, we make this a singleton list"""
        if obj.title:
            return [obj.title]
        else:
            return []

    def get_model(self):
        return models.Document
