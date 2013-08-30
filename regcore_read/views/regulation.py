from collections import defaultdict

from regcore import db
from regcore.responses import four_oh_four, success


def listing(request, label_id):
    """List versions of this regulation"""
    part = label_id.split('-')[0]
    notices = db.Notices().listing(label_id)
    by_date = defaultdict(list)
    for notice in (n for n in notices if 'effective_on' in n):
        by_date[notice['effective_on']].append(notice)
    reg_versions = set(db.Regulations().listing(label_id))

    regs = []
    for effective_date in sorted(by_date.keys(), reverse=True):
        notices = [(n['document_number'], n['effective_on'])
                   for n in by_date[effective_date]]
        notices = sorted(notices, reverse=True)
        found_latest = False
        for version, effective in ((v, d) for v, d in notices
                                   if v in reg_versions):
            if found_latest:
                regs.append({'version': version})
            else:
                found_latest = True
                regs.append({'version': version, 'by_date': effective})

    if regs:
        return success({'versions': regs})
    else:
        return four_oh_four()


def get(request, label_id, version):
    """Find and return the regulation with this version and label"""
    regulation = db.Regulations().get(label_id, version)
    if regulation:
        return success(regulation)
    else:
        return four_oh_four()
