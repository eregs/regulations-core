"""Each of the data structures relevant to the API (regulations, notices,
etc.), implemented using Django models"""
from django.core.exceptions import ObjectDoesNotExist

from regcore.models import Diff, Layer, Notice, Regulation


class DMRegulations(object):
    """Implementation of Django-models as regulations backend"""
    def get(self, label, version):
        """Find the regulation label + version"""
        try:
            reg = Regulation.objects.get(version=version,
                                         label_string=label)
            as_dict = {
                'label': reg.label_string.split('-'),
                'text': reg.text,
                'node_type': reg.node_type,
                'children': reg.children
            }
            if reg.title:
                as_dict['title'] = reg.title
            return as_dict
        except ObjectDoesNotExist:
            return None

    def _transform(self, reg, version):
        """Create the Django object"""
        return Regulation(version=version,
                          label_string='-'.join(reg['label']),
                          text=reg['text'],
                          title=reg.get('title', ''),
                          node_type=reg['node_type'],
                          root=(len(reg['label']) == 1),
                          children=reg['children'])

    def bulk_put(self, regs, version, root_label):
        """Store all reg objects"""
        # This does not handle subparts. Ignoring that for now
        Regulation.objects.filter(version=version,
                                  label_string__startswith=root_label).delete()
        Regulation.objects.bulk_create(map(
            lambda r: self._transform(r, version), regs), batch_size=100)

    def listing(self, label=None):
        """List regulation version-label pairs that match this label (or are
        root, if label is None)"""
        if label is None:
            query = Regulation.objects.filter(root=True)
        else:
            query = Regulation.objects.filter(label_string=label)

        query = query.only('version', 'label_string').order_by('version')
        # Flattens
        versions = [v for v in query.values_list('version', 'label_string')]
        return versions


class DMLayers(object):
    """Implementation of Django-models as layers backend"""
    def _transform(self, layer, version, layer_name):
        """Create a Django object"""
        layer = dict(layer)  # copy
        label_id = layer['label']
        del layer['label']
        return Layer(version=version, name=layer_name, label=label_id,
                     layer=layer)

    def bulk_put(self, layers, version, layer_name, root_label):
        """Store all layer objects"""
        # This does not handle subparts. Ignoring that for now
        Layer.objects.filter(version=version, name=layer_name,
                             label__startswith=root_label).delete()
        Layer.objects.bulk_create(map(
            lambda l: self._transform(l, version, layer_name), layers),
            batch_size=100)

    def get(self, name, label, version):
        """Find the layer that matches these parameters"""
        try:
            layer = Layer.objects.get(version=version, name=name,
                                      label=label)
            return layer.layer
        except ObjectDoesNotExist:
            return None


class DMNotices(object):
    """Implementation of Django-models as notice backend"""
    def put(self, doc_number, notice):
        """Store a single notice"""
        try:
            Notice.objects.get(document_number=doc_number).delete()
        except ObjectDoesNotExist:
            pass

        model = Notice(document_number=doc_number,
                       fr_url=notice['fr_url'],
                       publication_date=notice['publication_date'],
                       notice=notice)
        if 'effective_on' in notice:
            model.effective_on = notice['effective_on']
        for cfr_part in notice.get('cfr_parts', []):
            model.noticecfrpart_set.create(cfr_part=cfr_part)
        model.save()

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


class DMDiffs(object):
    """Implementation of Django-models as diff backend"""
    def put(self, label, old_version, new_version, diff):
        """Store a diff between two versions of a regulation node"""
        Diff.objects.filter(label=label, old_version=old_version,
                            new_version=new_version).delete()
        Diff(label=label, old_version=old_version, new_version=new_version,
             diff=diff).save()

    def get(self, label, old_version, new_version):
        """Find the associated diff"""
        try:
            diff = Diff.objects.get(label=label, old_version=old_version,
                                    new_version=new_version)
            return diff.diff
        except ObjectDoesNotExist:
            return None
