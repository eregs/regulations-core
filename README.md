regulations-core
================

[![Build Status](https://travis-ci.org/eregs/regulations-core.png)](https://travis-ci.org/eregs/regulations-core)

An engine that supplies the API that allows users to read regulations and
their various layers. 

This repository is part of a larger project. To read about it, please see 
[http://eregs.github.io/eregulations/](http://eregs.github.io/eregulations/).

## Features

* Search integration with Elastic Search or Django Haystack
* Support for storage via Elastic Search or Django Models
* Separation of API into a read and a write portion
* Destruction of regulations and layers into their components, allowing
  paragraph-level access
* Schema checking for regulations

## Requirements

Requirements are retrieved and/or build automatically via buildout (see
below).

* anyjson - Use Python's json or simplejson as available
* coverage - reports on test coverage
* django - Web framework
* django-haystack (1.2.7) - An interface for accessing Solr, Whoosh, and
  other search engines. This is only required if not using Elastic Search.
  Unfortunately, we are constrained to using the pre-rewrite version of
  haystack (though that may change in the future)
* django-nose - plugin for Django which allows for nose integration
* jsonschema - used to test that JSON provided fits our required data
  structure
* mock - makes constructing mock objects/functions easy
* nose - A pluggable test runner
* pyelasticsearch - required if using Elastic Search
* pysolr - required if using solr as a search backend
* south - Django's migration helper. Needed if using Django Models for
  storage
* zc.buildout - Tool used for building the application and handling
  dependencies

## API Docs

@todo (Replace with RTD when that's available)

## Buildout

Buildout is a simple tool for building and distributing python applications
quickly. We use it to get a version of the API up and running without
needing all of the fuss usually associated with setting up Django. Just run

```bash
$ pip install zc.buildout
$ buildout
```

After downloading the internet, you'll notice that some helpful scripts are
located in ```bin```, including ```bin/django``` and ```bin/test```. The
latter will run our test suite while the former is equivalent to running
manage.py in a traditional Django environment.

With that, you just need a few additional commands to get up and running:
```bash
$ ./bin/django syncdb
$ ./bin/django migrate
$ ./bin/django runserver
```

You'll be running (without search capability) using SQLite.

## Configurable Read and Write Endpoints

The read-only endpoints can be activated by delegating to *regcore.urls*
and turning on the *regcore* and *regcore_read*; write endpoints can be
activated by turning on *regcore_write*.

## Elastic Search For Data and Search

If *pyelasticsearch* is installed, you can use Elastic Search for all of
your needs. For a search endpoint, use *regcore_read.views.es_search.search* 
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

```python
BACKENDS = {
    'regulations': 'regcore.db.django_models.DMRegulations',
    'layers': 'regcore.db.django_models.DMLayers',
    'notices': 'regcore.db.django_models.DMNotices',
    'diffs': 'regcore.db.django_models.DMDiffs'
}
```

though this is also the default.

## Settings

If using Elastic Search, you will need to let the application know how to
connect to the search servers.

* ```ELASTIC_SEARCH_URLS``` - a list of strings which define how to connect
  to your search server(s). This is passed along to pyelasticsearch.
* ```ELASTIC_SEARCH_INDEX``` - the index to be used by elastic search. This
  defaults to 'eregs'

## Building the documentation

For most tweaks, you will simply need to run the Sphinx documentation
builder again.

```
$ ./bin/sphinx-build -b dirhtml -d docs/_build/doctrees/ docs/ docs/_build/dirhtml/
```

The output will be in ```docs/_build/dirhtml```.

If you are adding new modules, you may need to re-run the skeleton build
script first:

```
$ ./bin/sphinx-apidoc -F -o docs regcore
$ ./bin/sphinx-apidoc -F -o docs regcore_read
$ ./bin/sphinx-apidoc -F -o docs regcore_write
```

##  Running Tests

To run unit tests with buildout, simply run 

```bash
$ ./bin/test
```

This will include a report of test coverage.
