"""This delegates all GET tests to the DM Regulations tests"""

from datetime import date

from django.test import TestCase
from mock import patch

from regcore.db.splitter import *
from regcore.models import Diff, Layer, Notice, Regulation
from regcore.tests import db_django_models_tests as dm


class SplitterRegulationsTest(TestCase, dm.ReusableDMRegulations):
    def setUp(self):
        Regulation.objects.all().delete()
        self.dmr = SplitterRegulations()

    @patch('regcore.db.es.ElasticSearch')
    def test_bulk_put(self, es):
        sr = SplitterRegulations()
        nodes = [
            {'text': 'some text', 'label': ['111', '2'], 'children': [],
             'node_type': 'tyty'},
            {'text': 'other', 'label': ['111', '3'], 'children': [],
             'node_type': 'tyty2'}]
        sr.bulk_put(nodes, 'verver', '111')

        regs = Regulation.objects.all().order_by('text')

        self.assertEqual(2, len(regs))

        self.assertEqual('verver', regs[0].version)
        self.assertEqual('111-3', regs[0].label_string)
        self.assertEqual('other', regs[0].text)
        self.assertEqual('', regs[0].title)
        self.assertEqual('tyty2', regs[0].node_type)
        self.assertEqual([], regs[0].children)

        self.assertEqual('verver', regs[1].version)
        self.assertEqual('111-2', regs[1].label_string)
        self.assertEqual('some text', regs[1].text)
        self.assertEqual('', regs[1].title)
        self.assertEqual('tyty', regs[1].node_type)
        self.assertEqual([], regs[1].children)

        args = es.return_value.bulk_index.call_args[0]
        self.assertEqual(3, len(args))
        self.assertEqual('reg_tree', args[1])

        nodes[0]['version'] = 'verver'
        nodes[0]['label_string'] = '111-2'
        nodes[0]['id'] = 'verver/111-2'
        nodes[1]['version'] = 'verver'
        nodes[1]['label_string'] = '111-3'
        nodes[1]['id'] = 'verver/111-3'

        self.assertEqual(nodes, args[2])

    @patch('regcore.db.es.ElasticSearch')
    def test_bulk_put_overwrite(self, es):
        sr = SplitterRegulations()
        nodes = [{'text': 'other', 'label': ['111', '3'], 'children': [],
                  'node_type': 'tyty1'}]
        sr.bulk_put(nodes, 'verver', '111-3')

        regs = Regulation.objects.all()
        self.assertEqual(1, len(regs))
        self.assertEqual('tyty1', regs[0].node_type)

        nodes[0]['node_type'] = 'tyty2'

        sr.bulk_put(nodes, 'verver', '111-3')

        regs = Regulation.objects.all()
        self.assertEqual(1, len(regs))
        self.assertEqual('tyty2', regs[0].node_type)


class SplitterLayersTest(TestCase, dm.ReusableDMLayers):
    def setUp(self):
        Layer.objects.all().delete()
        self.dml = SplitterLayers()

    @patch('regcore.db.es.ElasticSearch')
    def test_bulk_put(self, es):
        layers = [
            {'111-22': [], '111-22-a': [], 'label': '111-22'},
            {'111-23': [], 'label': '111-23'}]
        SplitterLayers().bulk_put(layers, 'verver', 'name', '111')

        layer_models = Layer.objects.all().order_by('label')
        self.assertEqual(2, len(layer_models))

        self.assertEqual('verver', layer_models[0].version)
        self.assertEqual('name', layer_models[0].name)
        self.assertEqual('111-22', layer_models[0].label)
        self.assertEqual({'111-22': [], '111-22-a': []}, layer_models[0].layer)

        self.assertEqual('verver', layer_models[1].version)
        self.assertEqual('name', layer_models[1].name)
        self.assertEqual('111-23', layer_models[1].label)
        self.assertEqual({'111-23': []}, layer_models[1].layer)

        self.assertTrue(es.return_value.bulk_index.called)
        args = es.return_value.bulk_index.call_args[0]
        self.assertEqual(3, len(args))
        self.assertEqual('layer', args[1])

        del layers[0]['label']
        del layers[1]['label']
        transformed = [
            {'id': 'verver/name/111-22', 'version': 'verver',
             'name': 'name', 'label': '111-22', 'layer': layers[0]},
            {'id': 'verver/name/111-23', 'version': 'verver',
             'name': 'name', 'label': '111-23', 'layer': layers[1]}]

        self.assertEqual(transformed, args[2])

    @patch('regcore.db.es.ElasticSearch')
    def test_bulk_put_overwrite(self, es):
        layers = [{'111-23': [], 'label': '111-23'}]
        SplitterLayers().bulk_put(layers, 'verver', 'name', '111-23')

        layers = Layer.objects.all()
        self.assertEqual(1, len(layers))
        self.assertEqual({'111-23': []}, layers[0].layer)

        layers = [{'111-23': [1], 'label': '111-23'}]
        SplitterLayers().bulk_put(layers, 'verver', 'name', '111-23')

        layers = Layer.objects.all()
        self.assertEqual(1, len(layers))
        self.assertEqual({'111-23': [1]}, layers[0].layer)


class SplitterNoticesTest(TestCase, dm.ReusableDMNotices):
    def setUp(self):
        Notice.objects.all().delete()
        self.dmn = SplitterNotices()

    @patch('regcore.db.es.ElasticSearch')
    def test_put(self, es):
        sn = SplitterNotices()
        doc = {"some": "structure",
               'effective_on': '2011-01-01',
               'fr_url': 'http://example.com',
               'publication_date': '2010-02-02',
               'cfr_part': '222'}
        sn.put('docdoc', doc)

        notices = Notice.objects.all()
        self.assertEqual(1, len(notices))
        self.assertEqual('docdoc', notices[0].document_number)
        self.assertEqual(date(2011, 1, 1), notices[0].effective_on)
        self.assertEqual('http://example.com', notices[0].fr_url)
        self.assertEqual(date(2010, 2, 2), notices[0].publication_date)
        self.assertEqual('222', notices[0].cfr_part)
        self.assertEqual(doc, notices[0].notice)

        self.assertTrue(es.return_value.index.called)
        args, kwargs = es.return_value.index.call_args
        self.assertEqual(3, len(args))
        self.assertEqual('notice', args[1])
        self.assertEqual(doc, args[2])
        self.assertTrue('id' in kwargs)
        self.assertEqual('docdoc', kwargs['id'])

    @patch('regcore.db.es.ElasticSearch')
    def test_put_overwrite(self, es):
        sn = SplitterNotices()
        doc = {"some": "structure",
               'effective_on': '2011-01-01',
               'fr_url': 'http://example.com',
               'publication_date': '2010-02-02',
               'cfr_part': '222'}
        sn.put('docdoc', doc)

        notices = Notice.objects.all()
        self.assertEqual(1, len(notices))
        self.assertEqual('http://example.com', notices[0].fr_url)

        doc['fr_url'] = 'url2'
        sn.put('docdoc', doc)

        notices = Notice.objects.all()
        self.assertEqual(1, len(notices))
        self.assertEqual('url2', notices[0].fr_url)


class SplitterDiffTest(TestCase, dm.ReusableDMDiff):
    def setUp(self):
        Diff.objects.all().delete()
        self.dmd = SplitterDiffs()

    @patch('regcore.db.es.ElasticSearch')
    def test_put(self, es):
        sd = SplitterDiffs()
        sd.put('lablab', 'oldold', 'newnew', {"some": "structure"})

        diffs = Diff.objects.all()
        self.assertEqual(1, len(diffs))

        self.assertEqual('lablab', diffs[0].label)
        self.assertEqual('oldold', diffs[0].old_version)
        self.assertEqual('newnew', diffs[0].new_version)
        self.assertEqual({'some': 'structure'}, diffs[0].diff)

        self.assertTrue(es.return_value.index.called)
        args, kwargs = es.return_value.index.call_args
        self.assertEqual(3, len(args))
        self.assertEqual('diff', args[1])
        self.assertEqual('lablab/oldold/newnew', kwargs['id'])
        self.assertEqual({
            'label': 'lablab',
            'old_version': 'oldold',
            'new_version': 'newnew',
            'diff': {'some': 'structure'}
        }, args[2])

    @patch('regcore.db.es.ElasticSearch')
    def test_put_overwrite(self, es):
        sd = SplitterDiffs()
        sd.put('lablab', 'oldold', 'newnew', {"some": "structure"})

        diffs = Diff.objects.all()
        self.assertEqual(1, len(diffs))
        self.assertEqual({'some': 'structure'}, diffs[0].diff)

        sd.put('lablab', 'oldold', 'newnew', {"other": "structure"})
        diffs = Diff.objects.all()
        self.assertEqual(1, len(diffs))
        self.assertEqual({'other': 'structure'}, diffs[0].diff)
