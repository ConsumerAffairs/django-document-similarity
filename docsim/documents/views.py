from json import dumps

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .docsimserver import DocSimServer
from .models import Cluster, Document
from .serializers import ClusterSerializer  # , DocumentSerializer

ACCEPTED = 202


@csrf_exempt
@require_POST
def add_or_update(request):
    id = request.POST.get('id')
    text = request.POST.get('text')
    if id and text:
        Document(id=id, text=text).save()
        return HttpResponse(status=ACCEPTED)
    else:
        return HttpResponseBadRequest()


class ClusterList(ListAPIView):
    model = Cluster
    serializer_class = ClusterSerializer


class ClusterDetail(RetrieveAPIView):
    model = Cluster
    serializer_class = ClusterSerializer


@require_POST
def find_similar(request):
    id = request.POST.get('id')
    text = request.POST.get('text')
    if not text:
        return HttpResponseBadRequest()
    doc = Document(id=id, text=text)
    dss = DocSimServer()
    similar = dss.find_similar({'tokens': doc.tokens()}, max_results=10)
    return HttpResponse(content=dumps(similar), content_type='text/json')

# maybe later
#
#    if id:
#        doc.save()
#        dss.server.index([{'id': id, 'tokens': tokens}])
