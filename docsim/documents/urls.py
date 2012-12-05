from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ClusterDetail, ClusterList


urlpatterns = patterns(
    'documents.views',
    url(r'^add_or_update$', 'add_or_update', name='add_or_update'),
    url(r'^clusters$', ClusterList.as_view(), name='cluster-list'),
    url(r'^clusters/(?P<pk>\d+)$', ClusterDetail.as_view(),
        name='cluster-detail'),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
