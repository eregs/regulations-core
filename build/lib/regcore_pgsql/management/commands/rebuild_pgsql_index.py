import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from regcore.models import Document
from regcore_pgsql.models import DocumentIndex


logger = logging.getLogger(__name__)


def section_documents():
    return Document.objects\
        .filter(label_string__contains='-')\
        .exclude(label_string__regex=r'.*-.*-.*')


class Command(BaseCommand):
    help = "Rebuild document indexes for searching sections within Postgres"

    @transaction.atomic
    def handle(self, *args, **options):
        DocumentIndex.objects.all().delete()
        count = section_documents().count()
        for idx, document in enumerate(section_documents().iterator()):
            if idx % 100 == 0:
                logger.info('Inserted DocumentIndex %s / %s', idx, count)
            DocumentIndex.from_document(document).save()
        DocumentIndex.rebuild_search_vectors()
