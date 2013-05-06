# Copyright (C) 2013 Consumers Unified LLC
# Licensed under the GNU AGPL v3.0 - http://www.gnu.org/licenses/agpl.html

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'docsim.views.home', name='home'),
    # url(r'^docsim/', include('docsim.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # Uncomment to add the django rest framework browseable API login/logout
    # url(r'^api-auth/', include('rest_framework.urls',
    #                            namespace='rest_framework')),

    url(r'^documents/', include('documents.urls')),
)
