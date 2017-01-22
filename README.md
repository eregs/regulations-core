regulations-core
================
[![Build Status](https://travis-ci.org/eregs/regulations-core.svg?branch=master)](https://travis-ci.org/eregs/regulations-core)
[![Dependency Status](https://gemnasium.com/badges/github.com/eregs/regulations-core.svg)](https://gemnasium.com/github.com/eregs/regulations-core)
[![Coverage Status](https://coveralls.io/repos/github/eregs/regulations-core/badge.svg?branch=master)](https://coveralls.io/github/eregs/regulations-core?branch=master)
[![Code Climate](https://codeclimate.com/github/eregs/regulations-core/badges/gpa.svg)](https://codeclimate.com/github/eregs/regulations-core)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/0cdc7eb543724f60b428aa9cae42bd5f/badge.svg)](https://www.quantifiedcode.com/app/project/0cdc7eb543724f60b428aa9cae42bd5f)

An API that provides an interface for storing and retrieving regulations,
layers, etc.

This repository is part of a larger project. To read about it, please see
[http://eregs.github.io/](http://eregs.github.io/).

## Features

* Search integration with Elastic Search or Django Haystack
* Support for storage via Elastic Search or Django Models
* Separation of API into a read and a write portion
* Destruction of regulations and layers into their components, allowing
  paragraph-level access
* Schema checking for regulations

## Requirements

This application requires Python 2.7 (including PyPy), 3.3, 3.4, 3.5

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
* py.test - provides py.test as a test runner
* mock - makes constructing mock objects/functions easy
* pyelasticsearch - required if using Elastic Search
* flake8 - while not strictly required, we try to meet its standards
* pysolr - required if using solr as a search backend

## API Docs

[regulations-core on Read The Docs](http://regulations-core.readthedocs.org/en/latest/)

## Setup & Running

### Docker

For quick installation, consider installing from our
[Docker Image](https://hub.docker.com/r/eregs/core/). This image includes all
of the relevant dependencies, wrapped up in a "container" for ease of
installation. To run it, you'll need to have Docker installed, though the
installation instructions for [Linux](https://docs.docker.com/linux/step_one/),
[Mac](https://docs.docker.com/mac/step_one/), and
[Windows](https://docs.docker.com/windows/step_one/) are relatively painless.

The image is tailored for development purposes; it runs in DEBUG mode using
SQLite for data storage. To start it up, you'll want to run it in daemon mode,
forwarding port 8080:

```bash
docker run -p 8080:8080 -d eregs/core
```

Your server should now be running at http://localhost:8080/. Use docker
commands such as `docker ps`, `docker kill`, and `docker rm` to stop the
service. Note, however, that the database will disappear with the service.

### From Source

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

By default, you'll be using the settings defined in `regcore/settings/base.py`.
We recommend local modification be made in a `local_settings.py` file.

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

While we provide sane default settings in `regcore/settings/base.py`, we
recommend these defaults be overridden as needed in a `local_settings.py` file.

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

##  Importing Data

### Via the `eregs` parser

The `eregs` script (see
[regulations-parser](http://github.com/eregs/regulations-parser)) includes
subcommands which will write processed data to a running API. Notably, if
`write_to` (the last step of `pipeline`) is directed at a target beginning
with `http://` or `https://`, it will write the relevant data to that host.
Note that HTTP authentication can be encoded within these urls. For example,
if the API is running on the localhost, port 8000, you could run:

```bash
$ eregs write_to http://localhost:8000/
```

See the command line
[docs](https://eregs-parser.readthedocs.io/en/latest/commandline.html) for
more detail.

### Via the `import_docs` Django command

If you've already exported data from the parser, you may import it from the
command line with the `import_docs` Django management command. It should be
given the root directory of the data as its only parameter. Note that this
does not require a running API.

```bash
$ ls /path/to/data-root
diff  layer  notice  regulation
$ python manage.py import_docs /path/to/data-root
```

### Via curl

You may also simulate sending data to a running API via curl, if you've
exported data from the parser. For example, if the API is running on the
localhost, port 8000, you could run:

```bash
$ cd /path/to/data-root
$ ls
diff  layer  notice  regulation
$ for TAIL in $(find */* -type f | sort -r) \
do \
    curl -X PUT http://localhost:8000/$TAIL -d @$TAIL \
done
```

##  Running Tests

```bash
$ python manage.py test
```

This will include a report of test coverage.

To run tests across all supported python versions, run `tox`.

## Linting

We rely on flake8 for linting and style checks. You can run it over everything
via

```bash
$ flake8 .
```
