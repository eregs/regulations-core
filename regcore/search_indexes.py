from haystack.indexes import CharField, Indexable, MultiValueField, SearchIndex
from regcore.models import Regulation


class RegulationIndex(Indexable, SearchIndex):
    """Search index used by Haystack"""
    version = CharField(model_attr='version')
    label_string = CharField(model_attr='label_string')
    text = CharField(model_attr='text')
    title = MultiValueField()

    regulation = CharField(model_attr='label_string')
    text = CharField(document=True, use_template=True)

    def prepare_regulation(self, obj):
        return obj.label_string.split('-')[0]

    def prepare_title(self, obj):
        """For compatibility reasons, we make this a singleton list"""
        if obj.title:
            return [obj.title]
        else:
            return []

    def get_model(self):
        return Regulation
