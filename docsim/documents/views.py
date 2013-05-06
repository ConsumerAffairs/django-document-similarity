# Copyright (C) 2013 Consumers Unified LLC
# Licensed under the GNU AGPL v3.0 - http://www.gnu.org/licenses/agpl.html

from ujson import dumps

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .docsimserver import DocSimServer
from .forms import FindSimilarByIdForm, FindSimilarByTextForm
from .models import Cluster, Document
from .serializers import ClusterSerializer

ACCEPTED = 202
_dss = None


def dss():
    global _dss
    if not _dss:
        _dss = DocSimServer()
    return _dss


@csrf_exempt
@require_POST
def add_or_update(request):
    id = request.POST.get('id')
    text = request.POST.get('text')
    if id and text:
        doc = Document(id=id, text=text)
        doc.save()
        if request.POST.get('index'):
            dss().server.index([{'id': id, 'tokens': doc.tokens()}])
        return HttpResponse(status=ACCEPTED)
    else:
        return HttpResponseBadRequest()


class ClusterList(ListAPIView):
    model = Cluster
    serializer_class = ClusterSerializer


class ClusterDetail(RetrieveAPIView):
    model = Cluster
    serializer_class = ClusterSerializer


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def find_similar(request):
    defaults = {'min_score': .8, 'max_results': 10}
    if request.method == 'GET':
        defaults.update(request.GET.dict())
        form = FindSimilarByIdForm(defaults)
        if not form.is_valid():
            return HttpResponseBadRequest(dumps(form.errors))
        doc_id = form.cleaned_data['id']
        min_score = form.cleaned_data['min_score']
        max_results = form.cleaned_data['max_results']
        try:
            similar = dss().find_similar(doc_id, min_score=min_score,
                                         max_results=max_results)
        except ValueError:
            return HttpResponseBadRequest(u'document %s not in index' % doc_id)
    else:
        assert request.method == 'POST'
        defaults.update(request.POST.dict())
        form = FindSimilarByTextForm(defaults)
        if not form.is_valid():
            return HttpResponseBadRequest(dumps(form.errors))
        text = form.cleaned_data['text']
        min_score = form.cleaned_data['min_score']
        max_results = form.cleaned_data['max_results']
        doc = Document(text=text)
        tokens = doc.tokens()
        similar = dss().find_similar(
            {'tokens': tokens}, min_score=min_score, 
            max_results=max_results)
    return HttpResponse(content=dumps(similar), content_type='text/json')
