regulations-core
================

An engine that supplies the API that allows users to read regulations and their various layers. 

## Configurable Read and Write Endpoints

The read-only end points can be activated by delegating to *regcore.urls*
and turning on the *regcore* and *regcore_read*; write end points can be
activated by turning on *regcore_write*.

## Configuration-Dependent Libraries

This app can be configured with multiple backends. Elastic Search could be
used for both data and search; Django Models can be used for data; Haystack
(1.2.7) can be used for search (e.g. with Solr).

Optional libraries, then are

* django-haystack==1.2.7
* pyelasticsearch
* pysolr
* south

## Elastic Search For Data and Search

If *pyelasticsearch* is installed, you can use Elastic Search for all of
your needs. For a search end point, use *regcore_read.views.es_search.search* 
and use the following backend configuration:

```python
BACKENDS = {
    'regulations': 'regcore.db.es.ESRegulations',
    'layers': 'regcore.db.es.ESLayers',
    'notices': 'regcore.db.es.ESNotices',
    'diffs': 'regcore.db.es.ESDiffs'
}
```

## Django Models For Data, Elastic Search For Search

If *pyelasticsearch* and *south* are installed, you can combine django
models and Elastic Search. Use the *regcore_read.views.es_search.search* and
use the following backend configuration:

```python
BACKENDS = {
    'regulations': 'regcore.db.splitter.SplitterRegulations',
    'layers': 'regcore.db.splitter.SplitterLayers',
    'notices': 'regcore.db.splitter.SplitterNotices',
    'diffs': 'regcore.db.splitter.SplitterDiffs'
}
```

Be sure to also run south migration

## Django Models For Data, Haystack For Search

This is the default configuration. You will need to have *haystack* (1.2.7)
installed and *pysolr* (or *pyelasticsearch*). Use the
*regcore_read.views.haystack_search.search* as the endpoint and

``python
BACKENDS = {
    'regulations': 'regcore.db.django_models.DMRegulations',
    'layers': 'regcore.db.django_models.DMLayers',
    'notices': 'regcore.db.django_models.DMNotices',
    'diffs': 'regcore.db.django_models.DMDiffs'
}
```

though this is also the default.
