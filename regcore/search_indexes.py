from haystack.indexes import *
from haystack import site
from regcore.models import Regulation


class RegulationIndex(RealTimeSearchIndex):
    version = CharField(model_attr='version')
    label_string = CharField(model_attr='label_string')
    text = CharField(model_attr='text')
    title = CharField(model_attr='title')
    
    regulation = CharField(model_attr='label_string')
    text = CharField(document=True, use_template=True)

    def prepare_regulation(self, obj):
        return obj.label_string.split('-')[0]


site.register(Regulation, RegulationIndex)
