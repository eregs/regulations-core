"""Each of the data structures relevant to the API (regulations, notices,
etc.), implemented using Django models"""
import collections

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from regcore.db import interface
from regcore.models import Diff, Document, Layer, Notice


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


def build_adjacency_map(regs):
    """Build mapping from node IDs to child records
    :param regs: List of `Document` records
    """
    ret = collections.defaultdict(list)
    for reg in regs:
        if reg.parent_id is not None:
            ret[reg.parent_id].append(reg)
    return ret


def build_id(reg, version=None):
    if version is not None:
        return '{0}:{1}'.format(version, '-'.join(reg['label']))
    return '-'.join(reg['label'])


class DMDocuments(interface.Documents):
    """Implementation of Django-models as regulations backend"""
    def get(self, doc_type, label, version=None):
        """Find the regulation label + version"""
        regs = Document.objects.filter(
            doc_type=doc_type,
            label_string=label,
            version=version,
        ).get_descendants(
            include_self=True,
        )
        regs = list(regs.all())
        if not regs:
            return None
        adjacency_map = build_adjacency_map(regs)
        return self._serialize(regs[0], adjacency_map)

    def _serialize(self, reg, adjacency_map):
        ret = {
            'label': reg.label_string.split('-'),
            'text': reg.text,
            'node_type': reg.node_type,
            'children': [
                self._serialize(child, adjacency_map)
                for child in adjacency_map.get(reg.id, [])
            ],
        }
        ret['lft'] = getattr(reg, 'lft', None)
        if reg.title:
            ret['title'] = reg.title
        return ret

    def _transform(self, reg, doc_type, version=None):
        """Create the Django object"""
        return Document(
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

    def bulk_delete(self, doc_type, root_label, version):
        """Delete all documents that match these params"""
        # This does not handle subparts. Ignoring that for now
        Document.objects.filter(
            version=version,
            doc_type=doc_type,
            label_string__startswith=root_label,
        ).delete()

    def bulk_insert(self, regs, doc_type, version):
        """Store all document objects"""
        treeify(regs[0], Document.objects._get_next_tree_id())
        Document.objects.bulk_create(
            [self._transform(r, doc_type, version) for r in regs],
            batch_size=settings.BATCH_SIZE)

    def listing(self, doc_type, label=None):
        """List regulation version-label pairs that match this label (or are
        root, if label is None)"""
        if label is None:
            query = Document.objects.filter(doc_type=doc_type, root=True)
        else:
            query = Document.objects.filter(
                doc_type=doc_type, label_string=label)

        query = query.only('version', 'label_string').order_by('version')
        # Flattens
        versions = [v for v in query.values_list('version', 'label_string')]
        return versions


class DMLayers(interface.Layers):
    """Implementation of Django-models as layers backend"""
    def _transform(self, layer, layer_name, doc_type):
        """Create a Django object"""
        layer = dict(layer)  # copy
        doc_id = layer.pop('doc_id')
        return Layer(name=layer_name, layer=layer, doc_type=doc_type,
                     doc_id=doc_id)

    def bulk_delete(self, layer_name, doc_type, root_doc_id):
        """Delete all layer data matching the parameters"""
        # This does not handle subparts; Ignoring that for now
        # @todo - use regex to avoid deleting 222-11 when replacing 22
        Layer.objects.filter(name=layer_name, doc_type=doc_type,
                             doc_id__startswith=root_doc_id).delete()

    def bulk_insert(self, layers, layer_name, doc_type):
        """Store all layer objects"""
        Layer.objects.bulk_create(
            [self._transform(l, layer_name, doc_type) for l in layers],
            batch_size=settings.BATCH_SIZE)

    def get(self, name, doc_type, doc_id):
        """Find the layer that matches these parameters"""
        try:
            layer = Layer.objects.get(name=name, doc_type=doc_type,
                                      doc_id=doc_id)
            return layer.layer
        except ObjectDoesNotExist:
            return None


class DMNotices(interface.Notices):
    """Implementation of Django-models as notice backend"""
    def delete(self, doc_number):
        Notice.objects.filter(document_number=doc_number).delete()

    def insert(self, doc_number, notice):
        """Store a single notice"""
        model = Notice(document_number=doc_number,
                       fr_url=notice['fr_url'],
                       publication_date=notice['publication_date'],
                       notice=notice)
        if 'effective_on' in notice:
            model.effective_on = notice['effective_on']
        model.save()
        for cfr_part in notice.get('cfr_parts', []):
            model.noticecfrpart_set.create(cfr_part=cfr_part)

    def get(self, doc_number):
        """Find the associated notice"""
        try:
            return Notice.objects.get(
                document_number=doc_number).notice
        except ObjectDoesNotExist:
            return None

    def listing(self, part=None):
        """All notices or filtered by cfr_part"""
        query = Notice.objects
        if part:
            query = query.filter(noticecfrpart__cfr_part=part)
        results = query.values('document_number', 'effective_on', 'fr_url',
                               'publication_date')
        for result in results:
            for key in ('effective_on', 'publication_date'):
                if result[key]:
                    result[key] = result[key].isoformat()
                else:
                    del result[key]
        return list(results)  # maintain compatibility with other backends


class DMDiffs(interface.Diffs):
    """Implementation of Django-models as diff backend"""
    def insert(self, label, old_version, new_version, diff):
        """Store a diff between two versions of a regulation node"""
        Diff(label=label, old_version=old_version, new_version=new_version,
             diff=diff).save()

    def delete(self, label, old_version, new_version):
        Diff.objects.filter(label=label, old_version=old_version,
                            new_version=new_version).delete()

    def get(self, label, old_version, new_version):
        """Find the associated diff"""
        try:
            diff = Diff.objects.get(label=label, old_version=old_version,
                                    new_version=new_version)
            return diff.diff
        except ObjectDoesNotExist:
            return None
