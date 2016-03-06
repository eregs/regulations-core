from django.db import models

from regcore.fields import CompressedJSONField


class Regulation(models.Model):
    version = models.SlugField(max_length=20)
    label_string = models.SlugField(max_length=200)
    text = models.TextField()
    title = models.TextField(blank=True)
    node_type = models.SlugField(max_length=10)
    children = CompressedJSONField()
    root = models.BooleanField(default=False, db_index=True)

    class Meta:
        index_together = (('version', 'label_string'),)
        unique_together = (('version', 'label_string'),)


class Layer(models.Model):
    version = models.SlugField(max_length=20)
    name = models.SlugField(max_length=20)
    label = models.SlugField(max_length=200)
    layer = CompressedJSONField()

    class Meta:
        index_together = (('version', 'name', 'label'),)
        unique_together = (('version', 'name', 'label'),)


class Notice(models.Model):
    document_number = models.SlugField(max_length=20, primary_key=True)
    effective_on = models.DateField(null=True)
    fr_url = models.CharField(max_length=200, null=True)
    publication_date = models.DateField()
    notice = CompressedJSONField()


class NoticeCFRPart(models.Model):
    """Represents the one-to-many relationship between notices and CFR parts"""
    cfr_part = models.SlugField(max_length=10, db_index=True)
    notice = models.ForeignKey(Notice)

    class Meta:
        index_together = (('notice', 'cfr_part'),)
        unique_together = (('notice', 'cfr_part'),)


class Diff(models.Model):
    label = models.SlugField(max_length=200)
    old_version = models.SlugField(max_length=20)
    new_version = models.SlugField(max_length=20)
    diff = CompressedJSONField()

    class Meta:
        index_together = (('label', 'old_version', 'new_version'),)
        unique_together = (('label', 'old_version', 'new_version'),)


class Preamble(models.Model):
    """Represents the explanatory text associated with a notice"""
    document_number = models.SlugField(max_length=20, primary_key=True)
    data = CompressedJSONField()
