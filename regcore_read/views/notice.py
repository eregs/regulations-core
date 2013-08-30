from regcore import db
from regcore.responses import four_oh_four, success


def get(request, docnum):
    """Find and return the notice with this docnum"""
    notice = db.Notices().get(docnum)
    if notice:
        return success(notice)
    else:
        return four_oh_four()


def listing(request):
    """Find and return all notices"""
    return success({
        'results': db.Notices().listing(request.GET.get('part', None))
    })
