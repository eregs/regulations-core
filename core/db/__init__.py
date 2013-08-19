import es


class Regulations(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return es.ESRegulations()

    def get(self, label, version):
        """Documentation method. Returns a regulation node or None"""
        raise NotImplementedError

    def bulk_put(self, regs):
        """Documentation method. Add many entries, each with an id field"""
        raise NotImplementedError

    def listing(self, label):
        """Documentation method. List regulation versions that match this
        label"""
        raise NotImplementedError


class Layers(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return es.ESLayers()

    def bulk_put(self, layers):
        """Documentation method. Add many entries, each with an id field"""
        raise NotImplementedError

    def get(self, name, label, version):
        """Doc method. Return a single layer (no meta data) or None"""
        raise NotImplementedError


class Notices(object):
    """A level of indirection for our database abstraction. All backends
    should provide the same interface."""
    def __new__(cls):
        return es.ESNotices()

    def put(self, doc_number, notice):
        """Documentation method. doc_number:String, notice:Dict"""
        raise NotImplementedError

    def get(self, doc_number):
        """Documentation method. Return matching notice or None"""
        raise NotImplementedError

    def listing(self, part=None):
        """Documentation method. Return all notices or notices by part"""
        raise NotImplementedError
