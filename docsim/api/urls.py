from django.conf.urls import patterns, url

urlpatterns = patterns(
    'api.views',
    url(r'^buffer_html$', 'buffer_html_document', name='buffer_html'),
    url(r'^index$', 'index', name='index'),
)
