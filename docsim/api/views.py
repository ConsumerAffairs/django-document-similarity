from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import Pyro4

from .tokenizers import tokenize_html


ACCEPTED = 202


def get_service(name='gensim.testserver'):
    return Pyro4.Proxy(Pyro4.locateNS().lookup(name))


@csrf_exempt
@require_POST
def buffer_html_document(request):
    id = request.POST.get('id')
    html = request.POST.get('html')
    if id and html:
        tokens = tokenize_html(html)
        service = get_service()
        service.buffer([dict(id=id, tokens=tokens)])
        return HttpResponse(status=ACCEPTED)
    else:
        return HttpResponseBadRequest()


@csrf_exempt
@require_POST
def index(request):
    import ipdb; ipdb.set_trace()
    buffered = request.POST.get('buffered')
    if buffered:
        service = get_service()
        if request.POST.get('train'):
            service.train()
        service.index()
        return HttpResponse(dumps(dict(success=True)), 'application/json')
    else:
        # not implemented yet
        return HttpResponseBadRequest()

