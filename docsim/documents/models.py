from django.db import models
from django_extensions.db.fields.json import JSONField

from .tokenizers import tokenize_html


class Document(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    text = models.TextField()

    def __unicode__(self):
        return unicode(self.id)

    def tokens(self):
        return tokenize_html(self.text)


class Cluster(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    parameters = JSONField(default={})
    documents = models.ManyToManyField(Document, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.parameters)
