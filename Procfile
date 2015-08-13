web: python manage.py syncdb --migrate --settings=regcore.settings.cf && waitress-serve --port=$VCAP_APP_PORT regcore.settings.wsgi_cf:application
