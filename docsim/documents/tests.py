# -*- encoding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse
import mox

from .models import Document
from .tokenizers import force_ascii


class MockTestCase(TestCase):
    '''Base class for tests needing mock'''

    def setUp(self):
        super(MockTestCase, self).setUp()
        self.mox = mox.Mox()

    def tearDown(self):
        super(MockTestCase, self).tearDown()
        self.mox.VerifyAll()
        self.mox.UnsetStubs()


class ModelDocumentTest(TestCase):
    def test_str(self):
        doc = Document.objects.create(id='1', text='foo')
        self.assertEqual(str(doc), '1')

    def test_str_integer_id(self):
        doc = Document.objects.create(id=1, text='foo')
        self.assertEqual(str(doc), '1')

    def test_tokenize_html(self):
        doc = Document.objects.create(
            id=1, text='<p>a simple document</p>')
        self.assertEqual(doc.tokens(), ['simple', 'document'])


class TokenizerForceAsciiTest(TestCase):
    def test_plain_string(self):
        test = 'This is a plain string'
        self.assertEqual(test, force_ascii(test))

    def test_plain_unicode(self):
        test = u'This is a unicode string'
        self.assertEqual(str(test), force_ascii(test))

    def test_latin1_as_utf8(self):
        test = unicode('latin-1 is the bömb', 'latin-1').encode('utf-8')
        expected = 'latin-1 is the bmb'
        self.assertEqual(expected, force_ascii(test))


class ViewAddOrUpdateTest(TestCase):

    def test_add_doc(self):
        post = {
            'id': 1,
            'text': '<p>a simple document</p>'
        }
        self.assertFalse(Document.objects.exists())

        response = self.client.post(reverse('add_or_update'), post)

        self.assertEqual(response.status_code, 202)
        doc = Document.objects.get()
        self.assertEqual(doc.id, str(post['id']))
        self.assertEqual(doc.text, post['text'])

    def test_update_doc(self):
        Document.objects.create(id='3', text='foobar')
        post = {
            'id': 3,
            'text': '<p>baz</p>'
        }

        response = self.client.post(reverse('add_or_update'), post)

        self.assertEqual(response.status_code, 202)
        doc = Document.objects.get()
        self.assertEqual(doc.id, str(post['id']))
        self.assertEqual(doc.text, post['text'])

    def test_bad_request(self):
        response = self.client.post(reverse('add_or_update'), {})
        self.assertEqual(response.status_code, 400)