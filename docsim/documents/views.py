from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Cluster, Document
from .serializers import ClusterSerializer, DocumentSerializer

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
