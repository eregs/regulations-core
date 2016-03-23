class LayerParams(object):
    """We need to convert between an older form of url params,
        /layer/{layer type}/{reg label id}/{version id}
    and a new form:
        /layer/{layer type}/{doc type}/{doc id which may contain more slashes}
    This class handles that conversion and provides a single interface for
    both forms"""
    def __init__(self, doc_type, doc_id):
        # old format - we can remove once all data/libs are migrated
        if doc_type not in ('preamble', 'cfr'):
            # this looks backwards, but it's the format we assumed before
            label, version = doc_type, doc_id
            doc_type = 'cfr'
            doc_id = '/'.join([version, label])

        self.doc_type = doc_type
        self.doc_id = doc_id

    @property
    def tree_id(self):
        """Return "111_22" in both doc_ids, "111_22" and "version/111_22" """
        return self.doc_id.split('/')[-1]
