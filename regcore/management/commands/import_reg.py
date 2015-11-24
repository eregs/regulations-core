#!/usr/bin/env python

from __future__ import print_function

import requests
import os
import json
import urlparse
import logging

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from regcore_write.views import regulation, diff, layer, notice

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# This is an adaptation of the send_to.py script from regulations-stub as a
# management command to import files into the DB


class Command(BaseCommand):

    help = 'Import the regulation JSON into the database.'

    option_list = BaseCommand.option_list + (
        make_option(
            '-r',
            '--regulation',
            nargs=1,
            action='store',
            type=str,
            help='the specific regulation part number to upload (e.g.: 1026)'),

        make_option(
            '-s',
            '--stub-base',
            nargs=1,
            action='store',
            type=str,
            help=('the base filesystem path for regulations JSON (default: '
                  './stub)'),
            default=os.path.join(os.getcwd(), 'stub')),

        # note: because we're supporting Django 1.5, we are limited to using
        # optparse rather than the much better argparse. This means that we
        # can only accept one file per -f argument because there's no way to
        # accept an arbitrary number of arguments with optparse.
        make_option('-f',
                    '--files',
                    action='append',
                    type=str,
                    help='specific JSON files to upload',
                    default=[]),
    )

    def find_regulation_files(self, stub_base, regulation):
        """
        Find all JSON files in the `stub_base` belonging to the given
        `regulation`. Returns a list of paths relative to stub_base.
        """

        # regulations-parser outputs JSON files in the following directory
        # structure:
        #   regulation/
        #       [regulation part number]/
        #           [notice number]
        #           ...
        #   notice/
        #       [notice number]
        #       ...
        #   layer/
        #       [layer name]/
        #           [regulation part number]/
        #               [notice number]
        #               ...
        #   diff/
        #       [regulation part number]/
        #           [notice number]/
        #               [notice number]
        #               ...
        #

        regulation_files = []
        notice_names = None

        # Get the regulation/ JSON and notice numbers
        logger.info("getting files for regulation {}...".format(regulation))
        regulation_base = os.path.join(stub_base, 'regulation', regulation)
        if not os.path.isdir(regulation_base):
            logger.error("Can't find regulation JSON for {} at {}".format(
                regulation, regulation_base))
            return []
        for dirname, subdirs, files in os.walk(regulation_base):
            notice_names = files
            regulation_files.extend([os.path.join(dirname, f) for f in files])

        # Get notice JSON
        logger.info("getting notice files for regulation {}...".format(
            regulation))
        for dirname, subdirs, files in os.walk(
                os.path.join(stub_base, 'notice')):
            # Notices are not stored in a regulation-part-number
            # subdirectory. Use notice_names, from above, to just grab the
            # ones we want.
            notice_files = [os.path.join(dirname, f)
                            for f in files if f in notice_names]
            regulation_files.extend(notice_files)

        # Get layer JSON
        logger.info("getting layer files for regulation {}...".format(
            regulation))
        for dirname, subdirs, files in os.walk(
                os.path.join(stub_base, 'layer')):
            # For layers, dig into each subdirectory of the layer path until
            # we find one with our regulation part number.
            if dirname.endswith(regulation):
                layer_files = [os.path.join(dirname, f)
                               for f in files if f in notice_names]
                regulation_files.extend(layer_files)

        # Get diff JSON
        logger.info("getting diff files for regulation {}...".format(
            regulation))
        for dirname, subdirs, files in os.walk(
                os.path.join(stub_base, 'diff', regulation)):
            # For diffs, each regulation directory has a notice directory
            # with json files corrosponding to each other notice.
            diff_files = [os.path.join(dirname, f) for f in files]
            regulation_files.extend(diff_files)

        return regulation_files

    def send_to_server(self, api_base, stub_base, path):
        """
        Send the file at the given `path` to the given `api_base`. Path
        components will be appended to the `api_base` and are presumed to
        match.
        """
        relative_path = os.path.relpath(path, stub_base)
        url = urlparse.urljoin(api_base, relative_path)

        logger.info('sending {} to {}'.format(path, url))

        data = json.dumps(json.load(open(path, 'r')))
        r = requests.post(url, data=data,
                          headers={'content-type': 'application/json'})

        # regulations-core returns 204 on a successful POST
        if r.status_code != 204:
            logger.error("error sending {}: {}".format(
                r.status_code, r.reason))

    def add_arguments(self, parser):

        pass
        # this is a stub for when we go to argparse and can actually use it

    def handle(self, *args, **options):

        print(options)

        stub_base = options['stub_base']

        if options['regulation'] is None and options['files'] == []:
            raise CommandError('Must supply either a regulation to import or '
                               'a specific JSON file.')

        elif options['regulation'] is not None and options['files'] != []:
            raise CommandError('Cannot specify both regulation and files at '
                               'the same time.')

        elif options['regulation'] is None and options['files'] != []:
            files = [os.path.join(stub_base, f) for f in options['files']]

        elif options['regulation'] is not None and options['files'] == []:
            reg = options['regulation']
            files = self.find_regulation_files(stub_base, reg)

        # the request dummy is meant to fool the regcore_write api into
        # thinking that this is a request object

        class RequestDummy:
            def __init__(self):
                self.body = ''

        for f in files:
            data = json.dumps(json.load(open(f, 'r')))
            request = RequestDummy()
            request.body = data

            filename_data = f.replace(stub_base + '/', '').split('/')
            file_type = filename_data[0]

            if file_type == 'regulation':
                label = filename_data[1]
                version = filename_data[2]
                regulation.add(request, label, version)
            elif file_type == 'notice':
                version = filename_data[1]
                notice.add(request, version)
            elif file_type == 'layer':
                layer_type = filename_data[1]
                label = filename_data[2]
                version = filename_data[3]
                layer.add(request, layer_type, label, version)
            elif file_type == 'diff':
                label = filename_data[1]
                old_version = filename_data[2]
                new_version = filename_data[3]
                diff.add(request, label, old_version, new_version)
