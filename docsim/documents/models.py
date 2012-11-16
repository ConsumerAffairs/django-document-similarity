from django.db import models

from .tokenizers import tokenize_html


class Document(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    text = models.TextField()

    def __unicode__(self):
        return unicode(self.id)

    def tokens(self):
        return tokenize_html(self.text)
