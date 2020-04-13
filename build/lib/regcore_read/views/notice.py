from regcore.db import storage
from regcore.responses import four_oh_four, success


def get(request, docnum):
    """Find and return the notice with this docnum"""
    notice = storage.for_notices.get(docnum)
    if notice is not None:
        return success(notice)
    else:
        return four_oh_four()


def listing(request):
    """Find and return all notices"""
    return success({
        'results': storage.for_notices.listing(
            request.GET.get('part', None))
    })
