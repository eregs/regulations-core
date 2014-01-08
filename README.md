regulations-core
================

[![Build Status](https://travis-ci.org/eregs/regulations-core.png)](https://travis-ci.org/eregs/regulations-core)
[![Coverage Status](https://coveralls.io/repos/eregs/regulations-core/badge.png)](https://coveralls.io/r/eregs/regulations-core)

An API that provides an interface for storing and retrieving regulations,
layers, etc.

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
* django-haystack - An interface for accessing Solr, Whoosh, and other search
  engines. This is only required if not using Elastic Search. Unfortunately, 
  we are constrained to using the pre-rewrite version of haystack (though 
  that may change in the future)
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

[Read The Docs](http://regulations-core.readthedocs.org/en/latest/)

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

Buildout is configured (```buildout.cfg```) to use the
```example_settings.py``` settings. We recommend local modifications be made
in a ```local_settings.py``` file.

## Apps included

This repository contains three django apps, *regcore*, *regcore_read*, and
*regcore_write*. The former contains shared models and libraries. The "read"
app provides read-only end-points while the "write" app provides write-only
end-points. We recommend using *regcore.urls* as your url router, in which
case turning on or off read/write capabilities is as simple as including the
appropriate applications in your django settings file. Note that you will
always need *regcore* installed.


## Security

Note that *regcore_write* is designed to only be active inside an
organization; the assumption is that data will be pushed to public facing,
read-only (i.e. without *regcore_write*) sites separately.

When using the Elastic Search backend, data is passed as JSON, preventing
SQL-like injections. When using haystack, data is stored via django's model
framework, which escapes SQL before it hits the db.

All data types require JSON input (which is checked.) The regulation type
has an additional schema check, which is currently not present for other
data types. Again, this liability is limited by the segmentation of read and
write end points.

As all data is assumed to be publicly visible, data is not encrypted before
it is sent to the storage engine. Data may be compressed, however.

Be sure to override the default settings for both ```SECRET_KEY``` and to
turn ```DEBUG``` off in your ```local_settings.py```

## Storage-Backends

This project allows multiple backends for storing, retrieving, and searching
data. The default settings file uses django models for both data and search,
but django models can be combined with Elastic Search, or Elastic Search can
be used for both data and search. We discuss each configuration below.

### Django Models For Data, Haystack For Search

This is the default configuration. You will need to have *haystack*
installed and *pysolr* (or *pyelasticsearch*). This uses the
*regcore_read.views.haystack_search.search* as the endpoint and

```python
BACKENDS = {
    'regulations': 'regcore.db.django_models.DMRegulations',
    'layers': 'regcore.db.django_models.DMLayers',
    'notices': 'regcore.db.django_models.DMNotices',
    'diffs': 'regcore.db.django_models.DMDiffs'
}
```

Remember to run south migrations.

### Django Models For Data, Elastic Search For Search

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

### Elastic Search For Data and Search

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


## Settings

While we provide sane defaults in the ```example_settings.py``` file, we
recommend these defaults be overridden as needed in a
```local_settings.py``` file.

If using Elastic Search, you will need to let the application know how to
connect to the search servers.

* ```ELASTIC_SEARCH_URLS``` - a list of strings which define how to connect
  to your search server(s). This is passed along to pyelasticsearch.
* ```ELASTIC_SEARCH_INDEX``` - the index to be used by elastic search. This
  defaults to 'eregs'

The ```BACKENDS``` setting (as described above) must be a dictionary of the
appropriate model names ('regulations', 'layers', etc.) to the associated
backend class. Backends can be mixed and match, though I can't think of a
good use case for that desire.

All standard django and haystack settings are also available; you will
likely want to override ```DATABASES```, ```HAYSTACK_CONNECTIONS```,
```DEBUG``` and certainly ```SECRET_KEY```.

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
$ rm docs/regcore*.rst
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
