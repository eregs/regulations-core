# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    """The purpose of this migration is to enforce the correct character set
    and collation in mysql databases. We need utf8 to encode certain,
    non-latin characters and we need a case-sensitive collation so that we
    might have both 1005-A-b and 1005-A-B."""

    def _longtext(self, table, field):
        sql = ('ALTER TABLE regcore_%s MODIFY %s LONGTEXT '
               + 'CHARACTER SET utf8 COLLATE utf8_bin')
        db.execute(sql % (table, field))

    def _varchar(self, table, field, length):
        sql = ('ALTER TABLE regcore_%s MODIFY %s VARCHAR(%d) '
               + 'CHARACTER SET utf8 COLLATE utf8_bin')
        db.execute(sql % (table, field, length))

    def forwards(self, orm):
        if db.backend_name == 'mysql':
            table = 'diff'
            self._varchar(table, 'old_version', 20)
            self._varchar(table, 'new_version', 20)
            self._varchar(table, 'label', 50)
            self._longtext(table, 'diff')

            table = 'layer'
            self._varchar(table, 'version', 20)
            self._varchar(table, 'name', 20)
            self._varchar(table, 'label', 50)
            self._longtext(table, 'layer')

            table = 'notice'
            self._longtext(table, 'notice')

            table = 'regulation'
            self._varchar(table, 'version', 20)
            self._varchar(table, 'label_string', 50)
            self._longtext(table, 'text')
            self._longtext(table, 'title')
            self._longtext(table, 'children')
