regulations-core
================

[![Build Status](https://travis-ci.org/18F/regulations-core.png)](https://travis-ci.org/18F/regulations-core)
[![Coverage Status](https://coveralls.io/repos/18F/regulations-core/badge.svg?branch=master&service=github)](https://coveralls.io/github/18F/regulations-core?branch=master)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/0cdc7eb543724f60b428aa9cae42bd5f/badge.svg)](https://www.quantifiedcode.com/app/project/0cdc7eb543724f60b428aa9cae42bd5f)

An API that provides an interface for storing and retrieving regulations,
layers, etc.

This repository is part of a larger project. To read about it, please see 
[https://cfpb.github.io/eRegulations/](https://cfpb.github.io/eRegulations/).

## Features

* Search integration with Elastic Search or Django Haystack
* Support for storage via Elastic Search or Django Models
* Separation of API into a read and a write portion
* Destruction of regulations and layers into their components, allowing
  paragraph-level access
* Schema checking for regulations

## Requirements

Requirements are retrieved and/or build automatically via pip (see below).

* django - Web framework
* jsonschema - used to test that JSON provided fits our required data
  structure

The following libraries are optionally supported

* coverage - reports on test coverage
* django-haystack - An interface for accessing Solr, Whoosh, and other search
  engines. This is only required if not using Elastic Search. Unfortunately, 
  we are constrained to using the pre-rewrite version of haystack (though 
  that may change in the future)
* django-nose - plugin for Django which allows for nose integration
* mock - makes constructing mock objects/functions easy
* nose - A pluggable test runner
* pyelasticsearch - required if using Elastic Search
* flake8 - while not strictly required, we try to meet its standards
* pysolr - required if using solr as a search backend

## API Docs

[Read The Docs](http://regulations-core.readthedocs.org/en/latest/)

## Setup & Running

This project uses `requirements*.txt` files for defining dependencies, so you
can get up and running with `pip`:

```bash
$ pip install -r requirements.txt       # modules required for execution
$ pip install -r requirements_test.txt  # modules required for running tests
$ pip install -r requirements_dev.txt   # helpful modules for developers
```

With that, you just need a few additional commands to get up and running:
```bash
$ python manage.py migrate --fake-initial
$ python manage.py runserver
```

You'll be running (without search capability) using SQLite.

By default, you'll be using the `example_settings.py`. We recommend local
modification be made in a `local_settings.py` file.

## Apps included

This repository contains three Django apps, *regcore*, *regcore_read*, and
*regcore_write*. The former contains shared models and libraries. The "read"
app provides read-only end-points while the "write" app provides write-only
end-points (see the next section for security implications.) We recommend
using *regcore.urls* as your url router, in which case turning on or off
read/write capabilities is as simple as including the appropriate
applications in your Django settings file. Note that you will always need
*regcore* installed.


## Security

Note that *regcore_write* is designed to only be active inside an
organization; the assumption is that data will be pushed to public facing,
read-only (i.e. without *regcore_write*) sites separately.

When using the Elastic Search backend, data is passed as JSON, preventing
SQL-like injections. When using haystack, data is stored via Django's model
framework, which escapes SQL before it hits the db.

All data types require JSON input (which is checked.) The regulation type
has an additional schema check, which is currently not present for other
data types. Again, this liability is limited by the segmentation of read and
write end points.

As all data is assumed to be publicly visible, data is not encrypted before
it is sent to the storage engine. Data may be compressed, however.

Be sure to override the default settings for both `SECRET_KEY` and to
turn `DEBUG` off in your `local_settings.py`

## Storage-Backends

This project allows multiple backends for storing, retrieving, and searching
data. The default settings file uses Django models for both data and search,
but Django models can be combined with Elastic Search, or Elastic Search can
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

Remember to run migrations.

### Django Models For Data, Elastic Search For Search

If *pyelasticsearch* is installed, you can combine Django models and Elastic
Search. Use the *regcore_read.views.es_search.search* and use the following
backend configuration:

```python
BACKENDS = {
    'regulations': 'regcore.db.splitter.SplitterRegulations',
    'layers': 'regcore.db.splitter.SplitterLayers',
    'notices': 'regcore.db.splitter.SplitterNotices',
    'diffs': 'regcore.db.splitter.SplitterDiffs'
}
```

Be sure to also run migrations

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

While we provide sane defaults in the `example_settings.py` file, we recommend
these defaults be overridden as needed in a `local_settings.py` file.

If using Elastic Search, you will need to let the application know how to
connect to the search servers.

* `ELASTIC_SEARCH_URLS` - a list of strings which define how to connect
  to your search server(s). This is passed along to pyelasticsearch.
* `ELASTIC_SEARCH_INDEX` - the index to be used by elastic search. This
  defaults to 'eregs'

The `BACKENDS` setting (as described above) must be a dictionary of the
appropriate model names ('regulations', 'layers', etc.) to the associated
backend class. Backends can be mixed and matched, though I can't think of a
good use case for that desire.

All standard Django and haystack settings are also available; you will likely
want to override `DATABASES`, `HAYSTACK_CONNECTIONS`, `DEBUG` and certainly
`SECRET_KEY`.

## Building the documentation

For most tweaks, you will simply need to run the Sphinx documentation
builder again.

```bash
$ sphinx-build -b dirhtml -d docs/_build/doctrees/ docs/ docs/_build/dirhtml/
```

The output will be in `docs/_build/dirhtml`.

If you are adding new modules, you may need to re-run the skeleton build
script first:

```bash
$ rm docs/regcore*.rst
$ sphinx-apidoc -F -o docs regcore
$ sphinx-apidoc -F -o docs regcore_read
$ sphinx-apidoc -F -o docs regcore_write
```

##  Importing Regulation JSON

There is a `django_admin` command that facilitates the import of JSON
regulation content into the database. The command is called `import_reg` and
is used as follows, from the root `regcore` directory.

```bash
$ python manage.py import_reg -r <regulation-number> -s <path/to/stub/root>
```

For an example of JSON content, see `[regulations-stub](https://github.com/cfpb/regulations-stub/)`


##  Running Tests

```bash
$ python manage.py test
```

This will include a report of test coverage.

## Linting

We rely on flake8 for linting and style checks. You can run it over everything
via

```bash
$ flake8 .
```


