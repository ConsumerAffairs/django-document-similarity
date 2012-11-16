from django.conf.urls import patterns, url

urlpatterns = patterns(
    'documents.views',
    url(r'^add_or_update$', 'add_or_update', name='add_or_update'),
)
