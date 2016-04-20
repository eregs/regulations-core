from collections import defaultdict

from regcore.db import storage
from regcore.responses import four_oh_four, success


def listing(request, doc_type, label_id=None):
    """List versions of the requested (label_id) regulation; or all regulations
    if label_id is None"""
    if label_id:
        reg_versions = storage.for_documents.listing(doc_type, label_id)
        notices = storage.for_notices.listing(label_id.split('-')[0])
    else:
        reg_versions = storage.for_documents.listing(doc_type)
        notices = storage.for_notices.listing()

    by_date = defaultdict(list)
    for notice in (n for n in notices if 'effective_on' in n):
        by_date[notice['effective_on']].append(notice)

    regs = []
    for effective_date in sorted(by_date.keys(), reverse=True):
        notices = [(n['document_number'], n['effective_on'])
                   for n in by_date[effective_date]]
        notices = sorted(notices, reverse=True)
        found_latest = set()
        for doc_number, date in notices:
            for version, reg_part in reg_versions:
                if doc_number == version and reg_part in found_latest:
                    regs.append({'version': version, 'regulation': reg_part})
                elif doc_number == version:
                    found_latest.add(reg_part)
                    regs.append({'version': version, 'by_date': date,
                                 'regulation': reg_part})

    if regs:
        return success({'versions': regs})
    else:
        return four_oh_four()


def get(request, doc_type, label_id, version=None):
    """Find and return the regulation with this version and label"""
    regulation = storage.for_documents.get(doc_type, label_id, version)
    if regulation is not None:
        return success(regulation)
    else:
        return four_oh_four()
