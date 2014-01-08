from django.conf.urls import url
from django.http import Http404, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt


def by_verb_url(regex, name, by_verb):
    """Relatively clean way to segment url end points by HTTP Verb.
        @regex is the url regex as would be found in urls.py
        @name is also as would be found in urls.py
        @by_verb is a dictionary from verb (uppercase) to handler"""
    def wrapper(request, *args, **kwargs):
        verb = request.method.upper()
        if not by_verb:
            raise Http404
        elif verb in by_verb:
            return by_verb[verb](request, *args, **kwargs)
        else:
            return HttpResponseNotAllowed(by_verb.keys())
    if any(getattr(fn, 'csrf_exempt', False) for fn in by_verb.values()):
        wrapper = csrf_exempt(wrapper)

    return url(regex, wrapper, name=name)
