from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from regcore.fields import CompressedJSONField


class Document(MPTTModel):
    id = models.TextField(primary_key=True)     # noqa
    doc_type = models.SlugField(max_length=20)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True)
    version = models.SlugField(max_length=20, null=True, blank=True)
    label_string = models.SlugField(max_length=200)
    text = models.TextField()
    title = models.TextField(blank=True)
    node_type = models.SlugField(max_length=30)
    root = models.BooleanField(default=False, db_index=True)

    class Meta:
        index_together = (('doc_type', 'version', 'label_string'),)
        unique_together = (('doc_type', 'version', 'label_string'),)


class Layer(models.Model):
    name = models.SlugField(max_length=20)
    layer = CompressedJSONField()
    doc_type = models.SlugField(max_length=20)
    # We allow doc_ids to contain slashes, which are particularly important
    # for CFR docs, which use the [version_id]/[reg_label_id] format. It might
    # make sense to split off a version identifier into a separate field in
    # the future, if we can't treat that doc_id as an opaque string
    doc_id = models.SlugField(max_length=250)

    class Meta:
        index_together = (('name', 'doc_type', 'doc_id'),)
        unique_together = index_together


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
