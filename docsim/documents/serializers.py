# Copyright (C) 2013 Consumers Unified LLC
# Licensed under the GNU AGPL v3.0 - http://www.gnu.org/licenses/agpl.html

from rest_framework.serializers import ModelSerializer

from .models import Cluster, Document


class ClusterSerializer(ModelSerializer):
    class Meta:
        model = Cluster
        fields = ('id', 'created', 'documents')


class DocumentSerializer(ModelSerializer):
    class Meta:
        model = Document
