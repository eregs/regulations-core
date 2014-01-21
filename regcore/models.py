from django.db import models

from regcore.fields import CompressedJSONField


class Regulation(models.Model):
    version = models.SlugField(max_length=20)
    label_string = models.SlugField(max_length=50)
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
    label = models.SlugField(max_length=50)
    layer = CompressedJSONField()

    class Meta:
        index_together = (('version', 'name', 'label'),)
        unique_together = (('version', 'name', 'label'),)


class Notice(models.Model):
    document_number = models.SlugField(max_length=20, primary_key=True)
    effective_on = models.DateField(null=True)
    fr_url = models.CharField(max_length=200)
    publication_date = models.DateField()
    notice = CompressedJSONField()
    cfr_part = models.SlugField(max_length=10)


class Diff(models.Model):
    label = models.SlugField(max_length=50)
    old_version = models.SlugField(max_length=20)
    new_version = models.SlugField(max_length=20)
    diff = CompressedJSONField()

    class Meta:
        index_together = (('label', 'old_version', 'new_version'),)
        unique_together = (('label', 'old_version', 'new_version'),)
