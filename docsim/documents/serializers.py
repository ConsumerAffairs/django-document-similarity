from rest_framework.serializers import ModelSerializer

from .models import Cluster, Document


class ClusterSerializer(ModelSerializer):
    class Meta:
        model = Cluster
        fields = ('id', 'created', 'documents')


class DocumentSerializer(ModelSerializer):
    class Meta:
        model = Document
