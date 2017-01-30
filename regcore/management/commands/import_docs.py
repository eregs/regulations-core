import logging
import os

from django.core.management.base import BaseCommand
from django.test import Client, override_settings

logger = logging.getLogger(__name__)


def scoped_files(root):
    """Find all of the files which will need to be "uploaded"; trim them down
    to their suffix and separate their path components. We'll assume that
    `root` has no trailing slash"""
    for path, _, file_names in os.walk(root):
        for file_name in file_names:
            file_path = os.path.join(path, file_name)
            trimmed = file_path[len(root):]
            yield trimmed.split(os.sep)


def save_file(root, file_parts):
    """Given a file (indicated by a root file path and a set of file path
    components), read the file from disk and write it to the database. Log
    results."""
    file_path = os.path.join(root, *file_parts)
    with open(file_path, 'rb') as f:
        content = f.read()
    result = Client().put('/'.join(file_parts), data=content,
                          content_type='application/json')
    if result.status_code == 204:
        logger.info('Saved %s', file_path)
    else:
        logger.error('Failed to save %s: (%s), %s',
                     file_path, result.status_code, result.content[:100])


class Command(BaseCommand):
    help = "Import a collection of JSON files into the database."   # noqa

    def add_arguments(self, parser):
        parser.add_argument(
            'base_dir', default=os.getcwd(), nargs='?',
            help='the base filesystem path for importing JSON files'
        )

    @override_settings(ROOT_URLCONF='regcore.urls', ALLOWED_HOSTS=['*'])
    def handle(self, *args, **options):
        root = options['base_dir'].rstrip(os.sep)

        for file_parts in scoped_files(root):
            save_file(root, file_parts)
