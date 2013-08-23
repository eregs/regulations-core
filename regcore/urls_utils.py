from django.conf.urls import url
from django.http import HttpResponseNotAllowed

def by_verb_url(regex, name, **by_verb):
    def wrapper(request, *args, **kwargs):
        verb = request.method.upper()
        if verb in by_verb:
            return by_verb[verb](request, *args, **kwargs)
        else:
            return HttpResponseNotAllowed(by_verb.keys())
    return url(regex, wrapper, name=name)
