# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import mptt
import mptt.managers


def copy_regulations(apps, schema_editor):
    Regulation = apps.get_model('regcore', 'Regulation')
    Document = apps.get_model('regcore', 'Document')
    for reg in Regulation.objects.all():
        data = {
            field.name: getattr(reg, field.name)
            for field in Regulation._meta.fields
            if field.name not in {'parent'}
        }
        doc = Document(doc_type='cfr', **data)
        doc.parent_id = reg.parent_id
        doc.save()


def copy_preambles(apps, schema_editor):
    Preamble = apps.get_model('regcore', 'Preamble')
    Document = apps.get_model('regcore', 'Document')

    # Bind manager
    manager = mptt.managers.TreeManager()
    manager.model = Document
    mptt.register(Document)
    manager.contribute_to_class(Document, 'objects')

    for pre in Preamble.objects.all():
        write_node(Document, pre.data, 'preamble', pre.data['label'])


# Copy lightly modified import helpers

def write_node(Document, node, doc_type, label_id, version=None):

    to_save = []
    labels_seen = set()

    def add_node(node, parent=None):
        label_tuple = tuple(node['label'])
        labels_seen.add(label_tuple)

        node['parent'] = parent
        to_save.append(node)
        for child in node['children']:
            add_node(child, parent=node)
    add_node(node)

    DMDocuments(Document).bulk_put(to_save, doc_type, label_id, version)


def treeify(node, tree_id, pos=1, level=0):
    """Set tree properties in memory.
    """
    node['tree_id'] = tree_id
    node['level'] = level
    node['left'] = pos
    for child in node.get('children', []):
        pos = treeify(child, tree_id, pos=pos + 1, level=level + 1)
    pos = pos + 1
    node['right'] = pos
    return pos


def build_id(reg, version=None):
    if version is not None:
        return '{}:{}'.format(version, '-'.join(reg['label']))
    return '-'.join(reg['label'])


class DMDocuments(object):

    def __init__(self, Document):
        self.Document = Document

    def _transform(self, reg, doc_type, version=None):
        """Create the Django object"""
        return self.Document(
            id=build_id(reg, version),
            doc_type=doc_type,
            version=version,
            parent_id=(
                build_id(reg['parent'], version)
                if reg.get('parent')
                else None
            ),
            tree_id=reg['tree_id'],
            level=reg['level'],
            lft=reg['left'],
            rght=reg['right'],
            label_string='-'.join(reg['label']),
            text=reg['text'],
            title=reg.get('title', ''),
            node_type=reg['node_type'],
            root=(len(reg['label']) == 1),
        )

    def bulk_put(self, regs, doc_type, root_label, version):
        self.Document.objects.filter(
            version=version,
            doc_type=doc_type,
            label_string__startswith=root_label,
        ).delete()
        treeify(regs[0], self.Document.objects._get_next_tree_id())
        self.Document.objects.bulk_create(
            [self._transform(r, doc_type, version) for r in regs],
            batch_size=25)


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0011_create_document'),
    ]

    operations = [
        migrations.RunPython(copy_regulations),
        migrations.RunPython(copy_preambles),
    ]
