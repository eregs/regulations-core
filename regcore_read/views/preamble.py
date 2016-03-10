from regcore.db import storage
from regcore.responses import four_oh_four, success


def get(request, docnum):
    """Find and return the preamble with this docnum"""
    preamble = storage.for_preambles.get(docnum)
    if preamble is not None:
        return success(preamble)
    else:
        return four_oh_four()
